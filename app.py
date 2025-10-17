from flask import Flask, render_template, Blueprint, request, session, redirect, url_for, flash, jsonify
import test_handler
import os
import json

from neo4j import GraphDatabase

bp = Blueprint("test", __name__)



neo4j_uri, neo4j_user, neo4j_password = "bolt://localhost:7687", "neo4j", "testpassword"
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

with open("tests/emostate_demo.json", "r", encoding="utf-8") as f:
    test_json = json.load(f)

calculator = test_handler.TestScoreCalculator(test_json)
recommender = test_handler.RecommendationEngine(neo4j_uri, neo4j_user, neo4j_password)

app = Flask(__name__)
app.secret_key = os.urandom(24)

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

@app.route('/signin')
def signin():
    return render_template('signin.html')

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