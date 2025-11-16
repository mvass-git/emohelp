from flask import Flask, render_template, Blueprint, request, session, redirect, url_for, flash, jsonify
import test_handler
import os
import json
import db_manager.user_manager
import utils.token_manager

import services.user
import services.ontology


from db_manager.db import *

bp = Blueprint("test", __name__)





with open("tests/emostate_demo.json", "r", encoding="utf-8") as f:
    test_json = json.load(f)

calculator = test_handler.TestScoreCalculator(test_json)
recommender = test_handler.RecommendationEngine(neo4j_uri, neo4j_user, neo4j_password)

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.teardown_appcontext(close_db)

@app.route('/')
def index():
    return render_template('index.html')

def get_all_questions(test_data):
    """Extract all questions in order from test JSON"""
    questions = []
    for category in test_data['categories']:
        for question in category['questions']:
            questions.append({
                'id': question['id'],
                'text': question['text'],
                'scale_type': question.get('scale_type', test_data.get('answer_scale_type', 'frequency')),
                'reverse': question.get('reverse', False),
                'category': category['id']
            })
    return questions


@app.route('/test', methods=['GET'])
def test():
    """Start or restart the test"""
    # Clear previous session data
    session.pop('answers', None)
    session.pop('current_index', None)
    
    # Initialize session
    session['answers'] = {}
    session['current_index'] = 0
    
    return redirect(url_for('test_question'))


@app.route('/test/question', methods=['GET', 'POST'])
def test_question():
    if 'answers' not in session:
        session['answers'] = {}
    if 'current_index' not in session:
        session['current_index'] = 0

    questions = get_all_questions(test_json)
    current_index = session['current_index']

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Зберігаємо відповідь
        question_id = request.form.get('question_id')
        answer = request.form.get('answer')
        action = request.form.get('action', 'next')

        if answer and question_id:
            session['answers'][question_id] = int(answer)
            session.modified = True

        if action == 'back':
            current_index = max(0, current_index - 1)
        elif action in ('skip', 'next'):
            current_index += 1
        elif action == 'submit':
            return jsonify({'redirect': url_for('test_result')})

        session['current_index'] = current_index

        if current_index >= len(questions):
            return jsonify({'redirect': url_for('test_result')})

        current_question = questions[current_index]
        saved_answer = session['answers'].get(current_question['id'])

        html = render_template(
            'partials/question_block.html', 
            test=test_json,
            question=current_question,
            current_index=current_index,
            current_question=current_index + 1,
            total_questions=len(questions),
            saved_answer=saved_answer
        )

        return jsonify({'success': True, 'html': html})

    # GET-запит для початкового завантаження
    if current_index >= len(questions):
        return redirect(url_for('test_result'))

    current_question = questions[current_index]
    saved_answer = session['answers'].get(current_question['id'])

    return render_template(
        'test.html',
        test=test_json,
        question=current_question,
        current_index=current_index,
        current_question=current_index + 1,
        total_questions=len(questions),
        saved_answer=saved_answer
    )
@app.route("/test_result", methods=["GET"])
def test_result():
    """Calculate results and render the test result page."""
    
    # Get answers from session (not request.form!)
    answers = session.get('answers', {})
    if not answers:
        flash("No answers found. Please complete the test first.")
        return redirect(url_for("test_question"))
    
    # Calculate scores
    category_scores = calculator.compute_scores(answers)
    
    # Determine emotional states
    emotional_states = calculator.determine_emotional_states(category_scores)
    
    # Get state summary from recommender
    state_summary = recommender.get_state_summary(emotional_states)
    
    # Get related states
    related_states = recommender.get_related_states(emotional_states)
    
    # Get resource recommendations
    recommendations = recommender.get_recommendations(
        emotional_states, 
        limit=10
    )
    
    # Clear progress if needed (optional)
    session.pop('answers', None)
    session.pop('current_index', None)
    
    return render_template(
        "test_result.html",
        category_scores=category_scores,
        emotional_states=emotional_states,
        state_summary=state_summary,
        recommendations=recommendations,
        related_states=related_states
    )

@app.route("/rate_resource", methods=["POST"])
def rate_resource():
    test_id = request.form["test_id"]
    resource_id = request.form["resource_id"]
    rating = float(request.form["rating"])
    recommender.rate_resource(test_id, resource_id, rating)
    return "ok"

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signin', methods = ["GET", "POST"])
@services.user.redirect_if_logged_in("index.html")
def signin():
    if request.method == "GET":
        return render_template('sign_in.html')
    
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")

        result = services.user.authorize_user(login, password)
        if result["status"] == "success":
            return redirect(url_for("index"))
        else:
            return render_template("sign_in.html", error="Incorrect login or password")



@app.route('/signup', methods=['GET', 'POST'])
@services.user.redirect_if_logged_in("index.html")
def signup():
    if request.method == 'POST':
        login = request.form.get("login")
        country = request.form.get("country")
        birthday = request.form.get("date_of_birth")
        password = request.form.get("password")
        repassword = request.form.get("repassword")

        create_result = db_manager.user_manager.add_user(login, country, birthday, password, repassword)
        
        if create_result.get("status") == "success":
            auth_result = services.user.authorize_user(login, password)
            if auth_result["status"] == "success":
                return redirect(url_for("index"))

        return render_template('sign_up.html', countries=[1,2,3,4,10,15],
                               error="Registration failed or invalid data.")
    
    return render_template('sign_up.html', countries=[1,2,3,4,10,15])


@app.route("/admin", methods=["GET", "POST"])
@services.user.login_required(["admin"])
def admin():
    return render_template("admin_panel/admin.html")

@app.route('/api/graph')
def api_graph():
    """API endpoint для отримання даних графа"""
    try:
        graph_data = services.ontology.get_full_graph()
        return jsonify(graph_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/node/<int:node_id>')
def api_node_details(node_id):
    """API endpoint для отримання деталей вузла"""
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (n)
                WHERE id(n) = $node_id
                OPTIONAL MATCH (n)-[r]-(m)
                RETURN n, collect({rel: r, node: m}) as connections
            """, node_id=node_id)
            
            record = result.single()
            if not record:
                return jsonify({'error': 'Node not found'}), 404
            
            node = record['n']
            connections = []
            
            for c in record['connections']:
                try:
                    if c['rel']:
                        connections.append({
                            'relationship': c['rel'].type,
                            'node': {
                                'id': c['node'].id,
                                'label': c['node'].get('name', c['node'].get('title', 'Unknown')),
                                'type': list(c['node'].labels)[0] if c['node'].labels else 'Unknown'
                            }
                        })
                except Exception as e:
                    print(f"⚠️ Error processing connection: {str(e)}")
            
            return jsonify({
                'id': node.id,
                'labels': list(node.labels),
                'properties': dict(node),
                'connections': connections
            })
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500



@app.route('/api/schema')
def api_schema():
    """API endpoint для отримання схеми онтології"""
    try:
        with driver.session() as session:
            # Отримати всі типи вузлів
            node_types_result = session.run("""
                MATCH (n)
                RETURN DISTINCT labels(n)[0] as type
                ORDER BY type
            """)
            node_types = [record['type'] for record in node_types_result if record['type']]
            
            # Отримати всі типи зв'язків
            edge_types_result = session.run("""
                MATCH ()-[r]->()
                RETURN DISTINCT type(r) as type
                ORDER BY type
            """)
            edge_types = [record['type'] for record in edge_types_result]
            
            # Отримати властивості для кожного типу вузла
            node_properties = {}
            for node_type in node_types:
                props_result = session.run(f"""
                    MATCH (n:`{node_type}`)
                    WITH n LIMIT 1
                    RETURN keys(n) as properties
                """)
                record = props_result.single()
                if record:
                    node_properties[node_type] = record['properties']
            
            return jsonify({
                'node_types': node_types,
                'edge_types': edge_types,
                'node_properties': node_properties
            })
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@app.route('/api/node', methods=['POST'])
def api_create_node():
    """API endpoint для створення нового вузла"""
    try:
        data = request.get_json()
        node_type = data.get('type')
        properties = data.get('properties', {})
        
        if not node_type:
            return jsonify({'error': 'Node type is required'}), 400
        
        # Побудувати Cypher запит
        props_str = ', '.join([f"{k}: ${k}" for k in properties.keys()])
        query = f"CREATE (n:`{node_type}` {{{props_str}}}) RETURN id(n) as id, n"
        
        with driver.session() as session:
            result = session.run(query, **properties)
            record = result.single()
            
            node = record['n']
            return jsonify({
                'success': True,
                'node': {
                    'id': record['id'],
                    'type': node_type,
                    'properties': dict(node)
                }
            })
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@app.route('/api/edge', methods=['POST'])
def api_create_edge():
    """API endpoint для створення нового зв'язку"""
    try:
        data = request.get_json()
        from_id = data.get('from')
        to_id = data.get('to')
        edge_type = data.get('type')
        properties = data.get('properties', {})
        
        if not all([from_id, to_id, edge_type]):
            return jsonify({'error': 'from, to, and type are required'}), 400
        
        # Побудувати Cypher запит
        props_str = ', '.join([f"{k}: ${k}" for k in properties.keys()]) if properties else ''
        props_part = f" {{{props_str}}}" if props_str else ""
        
        query = f"""
            MATCH (a), (b)
            WHERE id(a) = $from_id AND id(b) = $to_id
            CREATE (a)-[r:`{edge_type}`{props_part}]->(b)
            RETURN id(r) as id, r
        """
        
        with driver.session() as session:
            result = session.run(query, from_id=from_id, to_id=to_id, **properties)
            record = result.single()
            
            if not record:
                return jsonify({'error': 'Nodes not found'}), 404
            
            rel = record['r']
            return jsonify({
                'success': True,
                'edge': {
                    'id': record['id'],
                    'type': edge_type,
                    'from': from_id,
                    'to': to_id,
                    'properties': dict(rel)
                }
            })
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@app.route('/api/edge/<int:edge_id>/properties', methods=['PUT'])
def api_update_edge_properties(edge_id):
    """API endpoint для оновлення властивостей зв'язку"""
    try:
        data = request.get_json()
        properties = data.get('properties', {})
        
        if not properties:
            return jsonify({'error': 'Properties are required'}), 400
        
        # Побудувати SET clause
        set_clauses = [f"r.{k} = ${k}" for k in properties.keys()]
        set_str = ', '.join(set_clauses)
        
        query = f"""
            MATCH ()-[r]->()
            WHERE id(r) = $edge_id
            SET {set_str}
            RETURN r
        """
        
        with driver.session() as session:
            result = session.run(query, edge_id=edge_id, **properties)
            record = result.single()
            
            if not record:
                return jsonify({'error': 'Edge not found'}), 404
            
            return jsonify({
                'success': True,
                'properties': dict(record['r'])
            })
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@app.route('/api/edge/<int:edge_id>', methods=['DELETE'])
def api_delete_edge(edge_id):
    """API endpoint для видалення зв'язку"""
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH ()-[r]->()
                WHERE id(r) = $edge_id
                DELETE r
                RETURN count(r) as deleted
            """, edge_id=edge_id)
            
            record = result.single()
            if record['deleted'] == 0:
                return jsonify({'error': 'Edge not found'}), 404
            
            return jsonify({'success': True, 'message': 'Edge deleted'})
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@app.route('/api/edge/<int:edge_id>', methods=['PUT'])
def api_update_edge(edge_id):
    """API endpoint для оновлення типу зв'язку"""
    try:
        data = request.get_json()
        new_type = data.get('type')
        
        if not new_type:
            return jsonify({'error': 'New type is required'}), 400
        
        with driver.session() as session:
            # Neo4j не дозволяє змінювати тип зв'язку напряму
            # Потрібно видалити старий і створити новий
            result = session.run("""
                MATCH (a)-[r]->(b)
                WHERE id(r) = $edge_id
                WITH a, b, properties(r) as props
                CREATE (a)-[new_r:`""" + new_type + """`]->(b)
                SET new_r = props
                RETURN id(new_r) as new_id
            """, edge_id=edge_id)
            
            record = result.single()
            if not record:
                return jsonify({'error': 'Edge not found'}), 404
            
            # Видалити старий зв'язок
            session.run("""
                MATCH ()-[r]->()
                WHERE id(r) = $edge_id
                DELETE r
            """, edge_id=edge_id)
            
            return jsonify({
                'success': True, 
                'message': 'Edge type updated',
                'new_id': record['new_id']
            })
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500



def find_static_and_templates():
    extra_dirs = ['templates', 'static']
    extra_files = []
    for d in extra_dirs:
        for dirname, _, files in os.walk(d):
            for filename in files:
                full_path = os.path.join(dirname, filename)
                extra_files.append(full_path)
    return extra_files

if __name__ == '__main__':
    app.run(debug=True, extra_files=find_static_and_templates())