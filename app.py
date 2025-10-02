from flask import Flask, jsonify, request
from services.tests import get_tests, get_test_by_id
from results.generator import generate_results

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Mental support service backend"})


@app.route("/api/tests", methods=["GET"])
def list_tests():
    """Повертає список доступних тестів"""
    return jsonify(get_tests())


@app.route("/api/tests/<test_id>", methods=["GET"])
def get_test(test_id):
    """Повертає структуру тесту (питання/відповіді)"""
    test = get_test_by_id(test_id)
    if not test:
        return jsonify({"error": "Test not found"}), 404
    return jsonify(test)


@app.route("/api/tests/<test_id>/submit", methods=["POST"])
def submit_test(test_id):
    """Приймає відповіді користувача і повертає результат"""
    data = request.json
    answers = data.get("answers", [])
    result = generate_results(test_id, answers)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
