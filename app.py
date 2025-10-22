from flask import Flask, render_template, Blueprint, request
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/test", methods=["GET", "POST"])
def test():
    if request.method == "GET":
        return render_template("test.html", test=test_json)
    
    elif request.method == "POST":
        # Get answers from form
        answers = {}
        for key, value in request.form.items():
            if key.startswith(('lon_', 'ex_', 'dep_', 'soc_', 'mot_')):
                answers[key] = int(value)
        
        # Calculate scores
        category_scores = calculator.compute_scores(answers)
        
        # Determine emotional states
        emotional_states = calculator.determine_emotional_states(category_scores)
        
        # Get state details
        state_summary = recommender.get_state_summary(emotional_states)
        
        # Get recommendations
        recommendations = recommender.get_recommendations(
            emotional_states, 
            limit=10
        )
        
        # Get related states
        related_states = recommender.get_related_states(emotional_states)
        
        # Optional: Get resources by specific themes
        # themes_of_interest = ['mindfulness', 'connection', 'activation']
        # themed_resources = recommender.get_resources_by_theme(themes_of_interest)
        
        return render_template(
            "test_result.html",
            category_scores=category_scores,
            emotional_states=emotional_states,
            state_summary=state_summary,
            recommendations=recommendations,
            related_states=related_states
        )

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signin')
def signin():
    return render_template('sign_in.html')

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