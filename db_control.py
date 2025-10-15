"""
Neo4j Ontology Loader Script
Loads the emotional state screening ontology into Neo4j database
"""

from neo4j import GraphDatabase
import os
from typing import Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Neo4jOntologyLoader:
    """Loader for emotional state screening ontology"""
    
    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize Neo4j connection
        
        Args:
            uri: Neo4j connection URI (e.g., 'bolt://localhost:7687')
            user: Database username
            password: Database password
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info(f"Connected to Neo4j at {uri}")
    
    def close(self):
        """Close database connection"""
        self.driver.close()
        logger.info("Connection closed")
    
    def clear_database(self, confirm: bool = False):
        """
        Clear all nodes and relationships from database
        
        Args:
            confirm: Must be True to actually clear the database
        """
        if not confirm:
            logger.warning("Database clear not confirmed. Skipping...")
            return
        
        with self.driver.session() as session:
            result = session.run("MATCH (n) DETACH DELETE n")
            logger.info("Database cleared")
    
    def execute_cypher_file(self, filepath: str):
        """
        Execute Cypher statements from a file
        
        Args:
            filepath: Path to .cypher or .cql file
        """
        logger.info(f"Loading Cypher file: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by semicolons and filter out comments and empty lines
        statements = []
        for statement in content.split(';'):
            # Remove comments
            lines = []
            for line in statement.split('\n'):
                # Remove line comments
                if '//' in line:
                    line = line[:line.index('//')]
                lines.append(line)
            
            statement = '\n'.join(lines).strip()
            
            # Skip empty statements and comments
            if statement and not statement.startswith('//'):
                statements.append(statement)
        
        logger.info(f"Found {len(statements)} Cypher statements")
        
        # Execute statements
        with self.driver.session() as session:
            for i, statement in enumerate(statements, 1):
                try:
                    session.run(statement)
                    logger.info(f"Executed statement {i}/{len(statements)}")
                except Exception as e:
                    logger.error(f"Error in statement {i}: {str(e)}")
                    logger.error(f"Statement: {statement[:100]}...")
                    raise
    
    def load_ontology(self):
        """Execute all ontology creation statements"""
        
        with self.driver.session() as session:
            logger.info("Creating Test Categories...")
            self._create_test_categories(session)
            
            logger.info("Creating Emotional States...")
            self._create_emotional_states(session)
            
            logger.info("Linking Categories to States...")
            self._link_categories_to_states(session)
            
            logger.info("Creating Resource Types...")
            self._create_resource_types(session)
            
            logger.info("Creating Themes...")
            self._create_themes(session)
            
            logger.info("Creating Sample Resources...")
            self._create_sample_resources(session)
            
            logger.info("Linking Resources to Types...")
            self._link_resources_to_types(session)
            
            logger.info("Linking States to Resources...")
            self._link_states_to_resources(session)
            
            logger.info("Linking Resources to Themes...")
            self._link_resources_to_themes(session)
            
            logger.info("Creating Cross-links between States...")
            self._create_state_relationships(session)
            
            logger.info("Ontology loaded successfully!")
    
    def _create_test_categories(self, session):
        """Create test category nodes"""
        categories = [
            {
                'id': 'loneliness',
                'name': 'Loneliness',
                'description': 'Feelings of isolation and lack of meaningful social connections',
                'weight': 1.0,
                'max_score': 20,
                'min_score': 4
            },
            {
                'id': 'existential',
                'name': 'Existential Anxiety',
                'description': 'Anxiety about life questions, meaning of existence, and choices',
                'weight': 1.0,
                'max_score': 20,
                'min_score': 4
            },
            {
                'id': 'depressive',
                'name': 'Depressive Symptoms',
                'description': 'Signs of depressed mood, apathy, and hopelessness',
                'weight': 1.0,
                'max_score': 20,
                'min_score': 4
            },
            {
                'id': 'social_connectedness',
                'name': 'Social Connectedness',
                'description': 'Sense of belonging to community and society',
                'weight': 1.0,
                'max_score': 20,
                'min_score': 4
            },
            {
                'id': 'motivation',
                'name': 'Motivation',
                'description': 'Level of energy, initiative, and capacity for action',
                'weight': 1.0,
                'max_score': 20,
                'min_score': 4
            }
        ]
        
        for cat in categories:
            session.run(
                """
                CREATE (c:TestCategory {
                    id: $id,
                    name: $name,
                    description: $description,
                    weight: $weight,
                    max_score: $max_score,
                    min_score: $min_score
                })
                """,
                **cat
            )
    
    def _create_emotional_states(self, session):
        """Create emotional state nodes"""
        states = [
            # Loneliness
            {'id': 'loneliness_low', 'name': 'Low Loneliness', 'level': 'low', 'severity': 1, 
             'score_range': '4-8', 'description': 'Healthy social integration, sense of belonging'},
            {'id': 'loneliness_medium', 'name': 'Moderate Loneliness', 'level': 'medium', 'severity': 2,
             'score_range': '9-14', 'description': 'Periodic feelings of loneliness, need for deeper connections'},
            {'id': 'loneliness_high', 'name': 'High Loneliness', 'level': 'high', 'severity': 3,
             'score_range': '15-20', 'description': 'Chronic social isolation, feeling disconnected'},
            
            # Existential
            {'id': 'existential_low', 'name': 'Low Existential Anxiety', 'level': 'low', 'severity': 1,
             'score_range': '4-8', 'description': 'Comfort with life questions, acceptance of uncertainty'},
            {'id': 'existential_medium', 'name': 'Moderate Existential Anxiety', 'level': 'medium', 'severity': 2,
             'score_range': '9-14', 'description': 'Periodic reflections on life meaning, searching for answers'},
            {'id': 'existential_high', 'name': 'High Existential Anxiety', 'level': 'high', 'severity': 3,
             'score_range': '15-20', 'description': 'Intense anxiety about death, meaning, and freedom of choice'},
            
            # Depressive
            {'id': 'depressive_low', 'name': 'Minimal Depressive Symptoms', 'level': 'low', 'severity': 1,
             'score_range': '4-8', 'description': 'Healthy emotional state, optimism'},
            {'id': 'depressive_medium', 'name': 'Mild Depressive Symptoms', 'level': 'medium', 'severity': 2,
             'score_range': '9-14', 'description': 'Periodic depressed mood, decreased energy'},
            {'id': 'depressive_high', 'name': 'Moderate to Severe Depressive Symptoms', 'level': 'high', 'severity': 3,
             'score_range': '15-20', 'description': 'Significant depressive symptoms requiring attention'},
            
            # Social
            {'id': 'social_low', 'name': 'Low Social Connectedness', 'level': 'low', 'severity': 3,
             'score_range': '4-8', 'description': 'Feeling alienated from society'},
            {'id': 'social_medium', 'name': 'Moderate Social Connectedness', 'level': 'medium', 'severity': 2,
             'score_range': '9-14', 'description': 'Partial social integration'},
            {'id': 'social_high', 'name': 'High Social Connectedness', 'level': 'high', 'severity': 1,
             'score_range': '15-20', 'description': 'Strong sense of belonging and integration'},
            
            # Motivation
            {'id': 'motivation_low', 'name': 'Low Motivation', 'level': 'low', 'severity': 3,
             'score_range': '4-8', 'description': 'Procrastination, lack of initiative'},
            {'id': 'motivation_medium', 'name': 'Moderate Motivation', 'level': 'medium', 'severity': 2,
             'score_range': '9-14', 'description': 'Unstable motivation, need for structure'},
            {'id': 'motivation_high', 'name': 'High Motivation', 'level': 'high', 'severity': 1,
             'score_range': '15-20', 'description': 'Proactivity, ability to structure activities'},
        ]
        
        for state in states:
            session.run(
                """
                CREATE (s:EmotionalState {
                    id: $id,
                    name: $name,
                    level: $level,
                    severity: $severity,
                    score_range: $score_range,
                    description: $description
                })
                """,
                **state
            )
    
    def _link_categories_to_states(self, session):
        """Create relationships between categories and states"""
        mappings = [
            ('loneliness', 'loneliness_'),
            ('existential', 'existential_'),
            ('depressive', 'depressive_'),
            ('social_connectedness', 'social_'),
            ('motivation', 'motivation_')
        ]
        
        for cat_id, state_prefix in mappings:
            session.run(
                """
                MATCH (c:TestCategory {id: $cat_id}), (s:EmotionalState)
                WHERE s.id STARTS WITH $state_prefix
                CREATE (c)-[:INDICATES {weight: 1.0}]->(s)
                """,
                cat_id=cat_id,
                state_prefix=state_prefix
            )
    
    def _create_resource_types(self, session):
        """Create resource type nodes"""
        types = [
            {'id': 'article', 'name': 'Article', 'description': 'Informational and educational articles'},
            {'id': 'book', 'name': 'Book', 'description': 'Literature for self-discovery'},
            {'id': 'video', 'name': 'Video', 'description': 'Video materials, lectures, TED talks'},
            {'id': 'film', 'name': 'Film', 'description': 'Feature and documentary films'},
            {'id': 'music', 'name': 'Music', 'description': 'Music collections and playlists'},
            {'id': 'exercise', 'name': 'Exercise', 'description': 'Practical exercises and techniques'},
            {'id': 'podcast', 'name': 'Podcast', 'description': 'Audio programs and conversations'},
            {'id': 'course', 'name': 'Online Course', 'description': 'Structured educational programs'}
        ]
        
        for rt in types:
            session.run(
                """
                CREATE (rt:ResourceType {
                    id: $id,
                    name: $name,
                    description: $description
                })
                """,
                **rt
            )
    
    def _create_themes(self, session):
        """Create theme nodes"""
        themes = [
            {'id': 'mindfulness', 'name': 'Mindfulness', 'description': 'Mindfulness and meditation practices'},
            {'id': 'connection', 'name': 'Connection', 'description': 'Building and deepening relationships'},
            {'id': 'meaning', 'name': 'Meaning', 'description': 'Finding life meaning and purpose'},
            {'id': 'self_compassion', 'name': 'Self-Compassion', 'description': 'Kind attitude toward oneself'},
            {'id': 'activation', 'name': 'Behavioral Activation', 'description': 'Increasing activity and engagement'},
            {'id': 'acceptance', 'name': 'Acceptance', 'description': 'Accepting uncertainty and reality'},
            {'id': 'community', 'name': 'Community', 'description': 'Participation in communities and groups'},
            {'id': 'creativity', 'name': 'Creativity', 'description': 'Creative self-expression'},
            {'id': 'routine', 'name': 'Routine & Structure', 'description': 'Creating structure and habits'},
            {'id': 'growth', 'name': 'Personal Growth', 'description': 'Self-development and self-improvement'}
        ]
        
        for theme in themes:
            session.run(
                """
                CREATE (t:Theme {
                    id: $id,
                    name: $name,
                    description: $description
                })
                """,
                **theme
            )
    
    def _create_sample_resources(self, session):
        """Create sample resource nodes"""
        resources = [
            {
                'id': 'r_loneliness_book_1',
                'title': 'Loneliness: Human Nature and the Need for Social Connection',
                'author': 'John T. Cacioppo',
                'description': 'Research on the nature of loneliness and ways to overcome it',
                'url': 'https://example.com/loneliness-book',
                'language': 'en',
                'rating': 4.5
            },
            {
                'id': 'r_loneliness_article_1',
                'title': 'How to Build Meaningful Connections',
                'author': 'Various',
                'description': 'Practical advice for creating deep relationships',
                'url': 'https://example.com/meaningful-connections',
                'language': 'en',
                'rating': 4.2
            },
            {
                'id': 'r_loneliness_exercise_1',
                'title': 'Social Reconnection Exercise',
                'description': '10-day program for gradually expanding social circle',
                'url': 'https://example.com/reconnection-exercise',
                'language': 'en',
                'duration_minutes': 15
            },
            {
                'id': 'r_existential_book_1',
                'title': "Man's Search for Meaning",
                'author': 'Viktor Frankl',
                'description': 'Classic work on finding meaning in any circumstances',
                'url': 'https://example.com/mans-search',
                'language': 'en',
                'rating': 4.9
            },
            {
                'id': 'r_existential_video_1',
                'title': 'Living with Uncertainty - TED Talk',
                'author': 'Speaker Name',
                'description': 'How to find peace in a world of uncertainty',
                'url': 'https://example.com/uncertainty-ted',
                'language': 'en',
                'duration_minutes': 18
            },
            {
                'id': 'r_depression_course_1',
                'title': 'Cognitive Behavioral Therapy for Depression',
                'description': 'Self-guided CBT-based course',
                'url': 'https://example.com/cbt-course',
                'language': 'en',
                'duration_minutes': 480
            },
            {
                'id': 'r_depression_music_1',
                'title': 'Uplifting Music Playlist',
                'description': 'Collection of mood-boosting music',
                'url': 'https://example.com/uplifting-playlist',
                'language': 'multi'
            },
            {
                'id': 'r_social_article_1',
                'title': 'Finding Your Community',
                'description': 'Guide to finding communities by interests',
                'url': 'https://example.com/find-community',
                'language': 'en'
            },
            {
                'id': 'r_motivation_book_1',
                'title': 'Atomic Habits',
                'author': 'James Clear',
                'description': 'How to build good habits and break bad ones',
                'url': 'https://example.com/atomic-habits',
                'language': 'en',
                'rating': 4.7
            },
            {
                'id': 'r_motivation_exercise_1',
                'title': 'Daily Planning Template',
                'description': 'Structured approach to organizing your day',
                'url': 'https://example.com/planning-template',
                'language': 'en'
            },
            {
                'id': 'r_universal_mindfulness_1',
                'title': 'Introduction to Mindfulness Meditation',
                'description': 'Basic meditation course for beginners',
                'url': 'https://example.com/mindfulness-intro',
                'language': 'en',
                'duration_minutes': 10
            },
            {
                'id': 'r_universal_film_1',
                'title': 'Inside Out',
                'description': 'Animated film about emotions and their role in life',
                'url': 'https://example.com/inside-out',
                'language': 'multi',
                'rating': 4.8
            }
        ]
        
        for resource in resources:
            # Build query dynamically based on available fields
            fields = ', '.join([f"{k}: ${k}" for k in resource.keys()])
            query = f"CREATE (r:Resource {{ {fields} }})"
            session.run(query, **resource)
    
    def _link_resources_to_types(self, session):
        """Link resources to resource types"""
        mappings = [
            ('_book_', 'book'),
            ('_article_', 'article'),
            ('_exercise_', 'exercise'),
            ('_video_', 'video'),
            ('_course_', 'course'),
            ('_music_', 'music'),
            ('_film_', 'film')
        ]
        
        for pattern, type_id in mappings:
            session.run(
                """
                MATCH (r:Resource), (rt:ResourceType {id: $type_id})
                WHERE r.id CONTAINS $pattern
                CREATE (r)-[:BELONGS_TO]->(rt)
                """,
                pattern=pattern,
                type_id=type_id
            )
    
    def _link_states_to_resources(self, session):
        """Link emotional states to helpful resources"""
        links = [
            # High loneliness
            ('loneliness_high', ['r_loneliness_book_1', 'r_loneliness_article_1', 
                                 'r_loneliness_exercise_1', 'r_social_article_1'], 'high', 0.8),
            # Moderate loneliness
            ('loneliness_medium', ['r_loneliness_article_1', 'r_social_article_1'], 'medium', 0.7),
            # High existential
            ('existential_high', ['r_existential_book_1', 'r_existential_video_1', 
                                  'r_universal_mindfulness_1'], 'high', 0.75),
            # Moderate existential
            ('existential_medium', ['r_existential_video_1', 'r_universal_mindfulness_1'], 'medium', 0.7),
            # High depressive
            ('depressive_high', ['r_depression_course_1', 'r_depression_music_1', 
                                'r_universal_mindfulness_1', 'r_motivation_exercise_1'], 'high', 0.8),
            # Moderate depressive
            ('depressive_medium', ['r_depression_music_1', 'r_motivation_book_1', 
                                  'r_universal_film_1'], 'medium', 0.65),
            # Low social
            ('social_low', ['r_social_article_1', 'r_loneliness_exercise_1'], 'high', 0.75),
            # Low motivation
            ('motivation_low', ['r_motivation_book_1', 'r_motivation_exercise_1', 
                               'r_depression_course_1'], 'high', 0.8),
            # Moderate motivation
            ('motivation_medium', ['r_motivation_book_1', 'r_motivation_exercise_1'], 'medium', 0.7),
        ]
        
        for state_id, resource_ids, priority, effectiveness in links:
            for resource_id in resource_ids:
                session.run(
                    """
                    MATCH (s:EmotionalState {id: $state_id}), (r:Resource {id: $resource_id})
                    CREATE (r)-[:HELPS_WITH {priority: $priority, effectiveness: $effectiveness}]->(s)
                    """,
                    state_id=state_id,
                    resource_id=resource_id,
                    priority=priority,
                    effectiveness=effectiveness
                )
    
    def _link_resources_to_themes(self, session):
        """Link resources to themes"""
        links = [
            ('r_universal_mindfulness_1', 'mindfulness'),
            ('r_loneliness_book_1', 'connection'),
            ('r_loneliness_article_1', 'connection'),
            ('r_loneliness_exercise_1', 'connection'),
            ('r_existential_book_1', 'meaning'),
            ('r_existential_video_1', 'meaning'),
            ('r_existential_video_1', 'acceptance'),
            ('r_depression_music_1', 'self_compassion'),
            ('r_motivation_book_1', 'activation'),
            ('r_motivation_exercise_1', 'activation'),
            ('r_motivation_exercise_1', 'routine'),
            ('r_depression_course_1', 'activation'),
            ('r_social_article_1', 'community'),
        ]
        
        for resource_id, theme_id in links:
            session.run(
                """
                MATCH (r:Resource {id: $resource_id}), (t:Theme {id: $theme_id})
                CREATE (r)-[:ADDRESSES]->(t)
                """,
                resource_id=resource_id,
                theme_id=theme_id
            )
    
    def _create_state_relationships(self, session):
        """Create relationships between related emotional states"""
        
        # Loneliness <-> Depression (same severity levels)
        session.run("""
            MATCH (s1:EmotionalState), (s2:EmotionalState)
            WHERE s1.id STARTS WITH 'loneliness_' 
              AND s2.id STARTS WITH 'depressive_'
              AND s1.severity = s2.severity
            CREATE (s1)-[:RELATED_TO {correlation: 0.65, type: 'comorbid'}]->(s2)
        """)
        
        # Low motivation <-> Depression (same severity levels)
        session.run("""
            MATCH (s1:EmotionalState), (s2:EmotionalState)
            WHERE s1.id STARTS WITH 'motivation_' 
              AND s2.id STARTS WITH 'depressive_'
              AND s1.severity = s2.severity
            CREATE (s1)-[:RELATED_TO {correlation: 0.7, type: 'comorbid'}]->(s2)
        """)
        
        # Low social connectedness <-> High loneliness
        session.run("""
            MATCH (s1:EmotionalState {id: 'social_low'}), 
                  (s2:EmotionalState {id: 'loneliness_high'})
            CREATE (s1)-[:RELATED_TO {correlation: 0.8, type: 'overlapping'}]->(s2)
        """)
        
        # Existential anxiety <-> Depression (same severity levels)
        session.run("""
            MATCH (s1:EmotionalState), (s2:EmotionalState)
            WHERE s1.id STARTS WITH 'existential_' 
              AND s2.id STARTS WITH 'depressive_'
              AND s1.severity = s2.severity
            CREATE (s1)-[:RELATED_TO {correlation: 0.6, type: 'comorbid'}]->(s2)
        """)
    
    def verify_ontology(self):
        """Verify that ontology was loaded correctly"""
        with self.driver.session() as session:
            # Count nodes by type
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(n) as count
                ORDER BY label
            """)
            
            logger.info("\n=== Node Counts ===")
            for record in result:
                logger.info(f"{record['label']}: {record['count']}")
            
            # Count relationships by type
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY type
            """)
            
            logger.info("\n=== Relationship Counts ===")
            for record in result:
                logger.info(f"{record['type']}: {record['count']}")


def main():
    """Main execution function"""
    
    # Database credentials - adjust as needed
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'testpassword')
    
    # Option to load from file or use built-in loader
    USE_FILE = False  # Set to True to load from .cypher file
    CYPHER_FILE = 'ontology.cypher'
    
    # Safety option - set to True to clear database before loading
    CLEAR_DATABASE = False
    
    try:
        loader = Neo4jOntologyLoader(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        
        # Clear database if requested
        if CLEAR_DATABASE:
            confirmation = input("Are you sure you want to clear the database? (yes/no): ")
            if confirmation.lower() == 'yes':
                loader.clear_database(confirm=True)
            else:
                logger.info("Database clear cancelled")
                return
        
        # Load ontology
        if USE_FILE:
            loader.execute_cypher_file(CYPHER_FILE)
        else:
            loader.load_ontology()
        
        # Verify results
        loader.verify_ontology()
        
        logger.info("\n✓ Ontology loaded successfully!")
        
    except Exception as e:
        logger.error(f"Error loading ontology: {str(e)}", exc_info=True)
        raise
    finally:
        loader.close()


if __name__ == "__main__":
    main()