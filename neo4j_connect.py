from neo4j import GraphDatabase

# Дані підключення
URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "testpassword")

driver = GraphDatabase.driver(URI, auth=AUTH)

def test_connection():
    with driver.session() as session:
        greeting = session.run("RETURN 'Connection successful' AS message").single()
        print(greeting["message"])

if __name__ == "__main__":
    test_connection()
