from neo4j import GraphDatabase
from typing import Dict, List, Tuple
import json
from uuid import uuid4
import datetime


class TestScoreCalculator:
    """Calculate test scores and determine emotional states"""
    
    def __init__(self, test_json):
        self.test_json = test_json
    
    def compute_scores(self, answers: Dict[str, int]) -> Dict[str, float]:
        """
        Compute category scores from test answers
        
        Args:
            answers: dict {question_id: value} (1..5)
        
        Returns:
            dict {category_id: score}
        """
        category_scores = {}
        
        for category in self.test_json["categories"]:
            cat_id = category["id"]
            scores = []
            
            for q in category["questions"]:
                qid = q["id"]
                val = int(answers.get(qid, 3))  # default middle value
                scale_type = q.get("scale_type", self.test_json.get("answer_scale_type", "frequency"))
                
                # Reverse scoring if needed
                if q.get("reverse", False):
                    val = 6 - val  # scale 1..5
                
                scores.append(val)
            
            # Calculate average score for category (range: 1-5)
            # Then scale to test range (4-20)
            avg_score = sum(scores) / len(scores)
            total_score = sum(scores)  # This is the actual score (4-20)
            
            category_scores[cat_id] = {
                'average': avg_score,
                'total': total_score,
                'question_count': len(scores)
            }
        
        return category_scores
    
    def determine_emotional_states(self, category_scores: Dict) -> List[str]:
        """
        Determine which emotional states apply based on scores
        
        Args:
            category_scores: dict from compute_scores()
        
        Returns:
            list of emotional state IDs
        """
        states = []
        
        for cat_id, score_data in category_scores.items():
            total_score = score_data['total']
            
            # Determine level based on score ranges
            # Low: 4-8, Medium: 9-14, High: 15-20
            if total_score <= 8:
                level = 'low'
            elif total_score <= 14:
                level = 'medium'
            else:
                level = 'high'
            
            # Map category to state ID
            if cat_id == 'social_connectedness':
                # For social connectedness, high score = positive state
                # So we reverse the interpretation
                if level == 'high':
                    level = 'high'  # Good
                elif level == 'low':
                    level = 'low'  # Bad
            
            if cat_id == 'motivation':
                # For motivation, high score = positive state
                # So we reverse the interpretation
                if level == 'low':
                    level = 'low'  # Bad
                elif level == 'high':
                    level = 'high'  # Good
            
            # Create state ID
            if cat_id == 'social_connectedness':
                state_id = f"social_{level}"
            elif cat_id == 'motivation':
                state_id = f"motivation_{level}"
            else:
                state_id = f"{cat_id}_{level}"
            
            states.append({
                'id': state_id,
                'category': cat_id,
                'level': level,
                'score': total_score
            })
        
        return states


class RecommendationEngine:
    """Generate resource recommendations based on emotional states"""
    
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    def close(self):
        self.driver.close()
    
    def get_recommendations(self, 
                          emotional_states: List[Dict], 
                          limit: int = 10,
                          min_priority: str = None) -> List[Dict]:
        """
        Get resource recommendations for given emotional states
        
        Args:
            emotional_states: list of state dicts with 'id', 'level', 'score'
            limit: maximum number of resources to return
            min_priority: filter by priority ('high', 'medium', 'low')
        
        Returns:
            list of recommended resources with metadata
        """
        # Extract state IDs
        state_ids = [state['id'] for state in emotional_states]
        
        # Prioritize high severity states
        high_priority_states = [
            state['id'] for state in emotional_states 
            if state['level'] == 'high' or 
            (state['level'] == 'low' and state['category'] in ['social_connectedness', 'motivation'])
        ]
        
        with self.driver.session() as session:
            # Query for resources that help with these states
            query = """
            MATCH (r:Resource)-[rel:HELPS_WITH]->(s:EmotionalState)
            WHERE s.id IN $state_ids
            
            // Get resource type
            OPTIONAL MATCH (r)-[:BELONGS_TO]->(rt:ResourceType)
            
            // Get themes
            OPTIONAL MATCH (r)-[:ADDRESSES]->(theme:Theme)
            
            WITH r, s, rel, rt, 
                 collect(DISTINCT theme.name) as themes,
                 CASE 
                    WHEN s.id IN $high_priority_states THEN 3
                    WHEN rel.priority = 'high' THEN 2
                    WHEN rel.priority = 'medium' THEN 1
                    ELSE 0
                 END as priority_score,
                 rel.effectiveness as effectiveness
            
            // Group by resource and aggregate
            WITH r, rt, themes,
                 collect(DISTINCT s.name) as addressed_states,
                 collect(DISTINCT s.id) as state_ids,
                 avg(effectiveness) as avg_effectiveness,
                 max(priority_score) as max_priority,
                 count(DISTINCT s) as state_count
            
            // Calculate final score
            WITH r, rt, themes, addressed_states, state_ids,
                 avg_effectiveness, max_priority, state_count,
                 (state_count * 10 + max_priority * 5 + avg_effectiveness * 10) as relevance_score
            
            RETURN 
                r.id as id,
                r.title as title,
                r.author as author,
                r.description as description,
                r.url as url,
                r.language as language,
                r.rating as rating,
                r.duration_minutes as duration_minutes,
                rt.name as resource_type,
                themes,
                addressed_states,
                state_ids,
                avg_effectiveness,
                max_priority,
                state_count,
                relevance_score
            
            ORDER BY relevance_score DESC, state_count DESC, avg_effectiveness DESC
            LIMIT $limit
            """
            
            result = session.run(
                query, 
                state_ids=state_ids,
                high_priority_states=high_priority_states,
                limit=limit
            )
            
            recommendations = [dict(record) for record in result]
            
            return recommendations
    
    def get_related_states(self, emotional_states: List[Dict]) -> List[Dict]:
        """
        Find related emotional states that might also need attention
        
        Args:
            emotional_states: list of current emotional states
        
        Returns:
            list of related states with correlation info
        """
        state_ids = [state['id'] for state in emotional_states]
        
        with self.driver.session() as session:
            query = """
            MATCH (s1:EmotionalState)-[r:RELATED_TO]->(s2:EmotionalState)
            WHERE s1.id IN $state_ids AND NOT s2.id IN $state_ids
            RETURN DISTINCT
                s2.id as id,
                s2.name as name,
                s2.description as description,
                s2.level as level,
                s2.severity as severity,
                r.correlation as correlation,
                r.type as relationship_type,
                collect(DISTINCT s1.name) as related_to
            ORDER BY r.correlation DESC, s2.severity DESC
            LIMIT 5
            """
            
            result = session.run(query, state_ids=state_ids)
            related = [dict(record) for record in result]
            
            return related
    
    def get_resources_by_theme(self, theme_ids: List[str], limit: int = 5) -> List[Dict]:
        """
        Get resources by specific themes
        
        Args:
            theme_ids: list of theme IDs
            limit: maximum number of resources
        
        Returns:
            list of resources
        """
        with self.driver.session() as session:
            query = """
            MATCH (r:Resource)-[:ADDRESSES]->(t:Theme)
            WHERE t.id IN $theme_ids
            
            OPTIONAL MATCH (r)-[:BELONGS_TO]->(rt:ResourceType)
            
            WITH r, rt, collect(DISTINCT t.name) as themes
            
            RETURN 
                r.id as id,
                r.title as title,
                r.author as author,
                r.description as description,
                r.url as url,
                r.language as language,
                r.rating as rating,
                rt.name as resource_type,
                themes
            
            ORDER BY r.rating DESC
            LIMIT $limit
            """
            
            result = session.run(query, theme_ids=theme_ids, limit=limit)
            return [dict(record) for record in result]
    
    def get_state_summary(self, emotional_states: List[Dict]) -> Dict:
        """
        Get detailed information about identified emotional states
        
        Args:
            emotional_states: list of emotional states
        
        Returns:
            dict with state details and statistics
        """
        state_ids = [state['id'] for state in emotional_states]
        
        with self.driver.session() as session:
            query = """
            UNWIND $state_ids as state_id
            MATCH (s:EmotionalState {id: state_id})
            OPTIONAL MATCH (s)<-[:INDICATES]-(c:TestCategory)
            
            RETURN 
                s.id as id,
                s.name as name,
                s.description as description,
                s.level as level,
                s.severity as severity,
                s.score_range as score_range,
                c.name as category
            """
            
            result = session.run(query, state_ids=state_ids)
            states_info = [dict(record) for record in result]
            
            # Calculate statistics
            severity_counts = {}
            for state in states_info:
                severity = state['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            return {
                'states': states_info,
                'total_count': len(states_info),
                'severity_distribution': severity_counts,
                'requires_attention': any(s['severity'] >= 2 for s in states_info)
            }
    def rate_resource(self, test_id, resource_id, rating):
        """
        Користувач оцінює ресурс після тесту.
        Оцінка впливає на вагу зв’язку між Resource і EmotionalState.
        """
        with self.driver.session() as session:
            session.run("""
            MATCH (t:TestResult {id: $test_id})-[:DETECTED]->(s:EmotionalState),
                (r:Resource {id: $resource_id})
            MERGE (t)-[rel:RATED]->(r)
            SET rel.rating = $rating, rel.rated_at = datetime()
            
            // Тепер оновлюємо вагу між станом і ресурсом
            MERGE (s)-[rec:RECOMMENDS]->(r)
            SET rec.weight = coalesce(rec.weight, 1.0) + ($rating - 3) * 0.1
            RETURN s, r, rec.weight AS new_weight
            """, test_id=test_id, resource_id=resource_id, rating=rating)
    
    def save_test_result(self, emotional_states, recommendations, answers=None, category_scores=None):
        """
        Зберігає результати проходження тесту в Neo4j (анонімно).
        """
        test_id = str(uuid4())
        timestamp = datetime.datetime.utcnow().isoformat()
        
        with self.driver.session() as session:
            session.run("""
            CREATE (t:TestResult {
                id: $test_id,
                created_at: datetime($timestamp),
                raw_answers: $answers_json,
                category_scores: $scores_json
            })
            WITH t
            UNWIND $state_ids as sid
            MATCH (s:EmotionalState {id: sid})
            CREATE (t)-[:DETECTED]->(s)
            WITH t
            UNWIND $rec_ids as rid
            MATCH (r:Resource {id: rid})
            CREATE (t)-[:RECOMMENDED]->(r)
            RETURN t
            """, 
            test_id=test_id,
            timestamp=timestamp,
            answers_json=json.dumps(answers or {}),
            scores_json=json.dumps(category_scores or {}),
            state_ids=[s["id"] for s in emotional_states],
            rec_ids=[r["id"] for r in recommendations]
            )
            
        return test_id