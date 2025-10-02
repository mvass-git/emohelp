import json

def load_tests():
    with open("tests_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_tests():
    tests = load_tests()
    return [{"id": t["id"], "title": t["title"], "description": t["description"]}
            for t in tests]

def get_test_by_id(test_id):
    tests = load_tests()
    for t in tests:
        if t["id"] == test_id:
            return t
    return None
