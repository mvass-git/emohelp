from db_manager.db import driver

def get_full_graph():
    """Отримати весь граф з Neo4j"""
    with driver.session() as session:
        result = session.run("""
            MATCH (n)
            OPTIONAL MATCH (n)-[r]->(m)
            RETURN n, r, m
        """)
        
        nodes = {}
        edges = []
        
        for record in result:
            # Додати початковий вузол
            node = record['n']
            if node.id not in nodes:
                nodes[node.id] = {
                    'id': node.id,
                    'label': node.get('name', node.get('title', node.get('id', 'Unknown'))),
                    'type': list(node.labels)[0] if node.labels else 'Unknown',
                    'properties': dict(node)
                }
            
            # Якщо є зв'язок і кінцевий вузол
            if record['r'] and record['m']:
                rel = record['r']
                end_node = record['m']
                
                # Додати кінцевий вузол
                if end_node.id not in nodes:
                    nodes[end_node.id] = {
                        'id': end_node.id,
                        'label': end_node.get('name', end_node.get('title', end_node.get('id', 'Unknown'))),
                        'type': list(end_node.labels)[0] if end_node.labels else 'Unknown',
                        'properties': dict(end_node)
                    }
                
                # Додати зв'язок
                edges.append({
                    'id': rel.id,
                    'from': node.id,
                    'to': end_node.id,
                    'label': rel.type,
                    'properties': dict(rel)
                })

        graph = {
            'nodes': list(nodes.values()),
            'edges': edges
        }

        print(graph)
        return graph