// Очищаємо базу (для тестового середовища)
MATCH (n) DETACH DELETE n;

// ====================================
// EMOTIONAL STATE SCREENING ONTOLOGY
// ====================================

// Очищення існуючих даних (опціонально)
// MATCH (n) DETACH DELETE n;

// ------------------------------------
// 1. СТВОРЕННЯ КАТЕГОРІЙ ТЕСТУ
// ------------------------------------

CREATE (loneliness:TestCategory {
  id: 'loneliness',
  name: 'Loneliness',
  description: 'Feelings of isolation and lack of meaningful social connections',
  weight: 1.0,
  max_score: 20,
  min_score: 4
});

CREATE (existential:TestCategory {
  id: 'existential',
  name: 'Existential Anxiety',
  description: 'Anxiety about life questions, meaning of existence, and choices',
  weight: 1.0,
  max_score: 20,
  min_score: 4
});

CREATE (depressive:TestCategory {
  id: 'depressive',
  name: 'Depressive Symptoms',
  description: 'Signs of depressed mood, apathy, and hopelessness',
  weight: 1.0,
  max_score: 20,
  min_score: 4
});

CREATE (social:TestCategory {
  id: 'social_connectedness',
  name: 'Social Connectedness',
  description: 'Sense of belonging to community and society',
  weight: 1.0,
  max_score: 20,
  min_score: 4
});

CREATE (motivation:TestCategory {
  id: 'motivation',
  name: 'Motivation',
  description: 'Level of energy, initiative, and capacity for action',
  weight: 1.0,
  max_score: 20,
  min_score: 4
});

// ------------------------------------
// 2. ЕМОЦІЙНІ СТАНИ (за рівнями)
// ------------------------------------

// Loneliness - levels
CREATE (lon_low:EmotionalState {
  id: 'loneliness_low',
  name: 'Low Loneliness',
  level: 'low',
  severity: 1,
  score_range: '4-8',
  description: 'Healthy social integration, sense of belonging'
});

CREATE (lon_medium:EmotionalState {
  id: 'loneliness_medium',
  name: 'Moderate Loneliness',
  level: 'medium',
  severity: 2,
  score_range: '9-14',
  description: 'Periodic feelings of loneliness, need for deeper connections'
});

CREATE (lon_high:EmotionalState {
  id: 'loneliness_high',
  name: 'High Loneliness',
  level: 'high',
  severity: 3,
  score_range: '15-20',
  description: 'Chronic social isolation, feeling disconnected'
});

// Existential anxiety - levels
CREATE (ex_low:EmotionalState {
  id: 'existential_low',
  name: 'Low Existential Anxiety',
  level: 'low',
  severity: 1,
  score_range: '4-8',
  description: 'Comfort with life questions, acceptance of uncertainty'
});

CREATE (ex_medium:EmotionalState {
  id: 'existential_medium',
  name: 'Moderate Existential Anxiety',
  level: 'medium',
  severity: 2,
  score_range: '9-14',
  description: 'Periodic reflections on life meaning, searching for answers'
});

CREATE (ex_high:EmotionalState {
  id: 'existential_high',
  name: 'High Existential Anxiety',
  level: 'high',
  severity: 3,
  score_range: '15-20',
  description: 'Intense anxiety about death, meaning, and freedom of choice'
});

// Depressive symptoms - levels
CREATE (dep_low:EmotionalState {
  id: 'depressive_low',
  name: 'Minimal Depressive Symptoms',
  level: 'low',
  severity: 1,
  score_range: '4-8',
  description: 'Healthy emotional state, optimism'
});

CREATE (dep_medium:EmotionalState {
  id: 'depressive_medium',
  name: 'Mild Depressive Symptoms',
  level: 'medium',
  severity: 2,
  score_range: '9-14',
  description: 'Periodic depressed mood, decreased energy'
});

CREATE (dep_high:EmotionalState {
  id: 'depressive_high',
  name: 'Moderate to Severe Depressive Symptoms',
  level: 'high',
  severity: 3,
  score_range: '15-20',
  description: 'Significant depressive symptoms requiring attention'
});

// Social connectedness - levels
CREATE (soc_low:EmotionalState {
  id: 'social_low',
  name: 'Low Social Connectedness',
  level: 'low',
  severity: 3,
  score_range: '4-8',
  description: 'Feeling alienated from society'
});

CREATE (soc_medium:EmotionalState {
  id: 'social_medium',
  name: 'Moderate Social Connectedness',
  level: 'medium',
  severity: 2,
  score_range: '9-14',
  description: 'Partial social integration'
});

CREATE (soc_high:EmotionalState {
  id: 'social_high',
  name: 'High Social Connectedness',
  level: 'high',
  severity: 1,
  score_range: '15-20',
  description: 'Strong sense of belonging and integration'
});

// Motivation - levels
CREATE (mot_low:EmotionalState {
  id: 'motivation_low',
  name: 'Low Motivation',
  level: 'low',
  severity: 3,
  score_range: '4-8',
  description: 'Procrastination, lack of initiative'
});

CREATE (mot_medium:EmotionalState {
  id: 'motivation_medium',
  name: 'Moderate Motivation',
  level: 'medium',
  severity: 2,
  score_range: '9-14',
  description: 'Unstable motivation, need for structure'
});

CREATE (mot_high:EmotionalState {
  id: 'motivation_high',
  name: 'High Motivation',
  level: 'high',
  severity: 1,
  score_range: '15-20',
  description: 'Proactivity, ability to structure activities'
});

// ------------------------------------
// 3. ЗВ'ЯЗКИ: КАТЕГОРІЇ -> СТАНИ
// ------------------------------------

MATCH (c:TestCategory {id: 'loneliness'}), (s:EmotionalState)
WHERE s.id STARTS WITH 'loneliness_'
CREATE (c)-[:INDICATES {weight: 1.0}]->(s);

MATCH (c:TestCategory {id: 'existential'}), (s:EmotionalState)
WHERE s.id STARTS WITH 'existential_'
CREATE (c)-[:INDICATES {weight: 1.0}]->(s);

MATCH (c:TestCategory {id: 'depressive'}), (s:EmotionalState)
WHERE s.id STARTS WITH 'depressive_'
CREATE (c)-[:INDICATES {weight: 1.0}]->(s);

MATCH (c:TestCategory {id: 'social_connectedness'}), (s:EmotionalState)
WHERE s.id STARTS WITH 'social_'
CREATE (c)-[:INDICATES {weight: 1.0}]->(s);

MATCH (c:TestCategory {id: 'motivation'}), (s:EmotionalState)
WHERE s.id STARTS WITH 'motivation_'
CREATE (c)-[:INDICATES {weight: 1.0}]->(s);

// ------------------------------------
// 4. ТИПИ РЕСУРСІВ
// ------------------------------------

CREATE (rt_article:ResourceType {
  id: 'article',
  name: 'Article',
  description: 'Informational and educational articles'
});

CREATE (rt_book:ResourceType {
  id: 'book',
  name: 'Book',
  description: 'Literature for self-discovery'
});

CREATE (rt_video:ResourceType {
  id: 'video',
  name: 'Video',
  description: 'Video materials, lectures, TED talks'
});

CREATE (rt_film:ResourceType {
  id: 'film',
  name: 'Film',
  description: 'Feature and documentary films'
});

CREATE (rt_music:ResourceType {
  id: 'music',
  name: 'Music',
  description: 'Music collections and playlists'
});

CREATE (rt_exercise:ResourceType {
  id: 'exercise',
  name: 'Exercise',
  description: 'Practical exercises and techniques'
});

CREATE (rt_podcast:ResourceType {
  id: 'podcast',
  name: 'Podcast',
  description: 'Audio programs and conversations'
});

CREATE (rt_course:ResourceType {
  id: 'course',
  name: 'Online Course',
  description: 'Structured educational programs'
});

// ------------------------------------
// 5. ТЕМИ (для перехресних зв'язків)
// ------------------------------------

CREATE (t_mindfulness:Theme {
  id: 'mindfulness',
  name: 'Mindfulness',
  description: 'Mindfulness and meditation practices'
});

CREATE (t_connection:Theme {
  id: 'connection',
  name: 'Connection',
  description: 'Building and deepening relationships'
});

CREATE (t_meaning:Theme {
  id: 'meaning',
  name: 'Meaning',
  description: 'Finding life meaning and purpose'
});

CREATE (t_self_compassion:Theme {
  id: 'self_compassion',
  name: 'Self-Compassion',
  description: 'Kind attitude toward oneself'
});

CREATE (t_activation:Theme {
  id: 'activation',
  name: 'Behavioral Activation',
  description: 'Increasing activity and engagement'
});

CREATE (t_acceptance:Theme {
  id: 'acceptance',
  name: 'Acceptance',
  description: 'Accepting uncertainty and reality'
});

CREATE (t_community:Theme {
  id: 'community',
  name: 'Community',
  description: 'Participation in communities and groups'
});

CREATE (t_creativity:Theme {
  id: 'creativity',
  name: 'Creativity',
  description: 'Creative self-expression'
});

CREATE (t_routine:Theme {
  id: 'routine',
  name: 'Routine & Structure',
  description: 'Creating structure and habits'
});

CREATE (t_growth:Theme {
  id: 'growth',
  name: 'Personal Growth',
  description: 'Self-development and self-improvement'
});

// ------------------------------------
// 6. ПРИКЛАДИ РЕСУРСІВ (заповнювачі)
// ------------------------------------

// Ресурси для високої самотності
CREATE (r1:Resource {
  id: 'r_loneliness_book_1',
  title: 'Loneliness: Human Nature and the Need for Social Connection',
  title_ua: 'Самотність: людська природа та потреба в соціальному зв\'язку',
  author: 'John T. Cacioppo',
  description: 'Дослідження природи самотності та шляхів її подолання',
  url: 'https://example.com/loneliness-book',
  language: 'en',
  rating: 4.5,
  created_at: datetime()
});

CREATE (r2:Resource {
  id: 'r_loneliness_article_1',
  title: 'How to Build Meaningful Connections',
  title_ua: 'Як будувати значущі зв\'язки',
  author: 'Various',
  description: 'Практичні поради для створення глибоких стосунків',
  url: 'https://example.com/meaningful-connections',
  language: 'uk',
  rating: 4.2,
  created_at: datetime()
});

CREATE (r3:Resource {
  id: 'r_loneliness_exercise_1',
  title: 'Social Reconnection Exercise',
  title_ua: 'Вправа на відновлення соціальних зв\'язків',
  description: '10-денна програма для поступового розширення соціального кола',
  url: 'https://example.com/reconnection-exercise',
  language: 'uk',
  duration_minutes: 15,
  created_at: datetime()
});

// Ресурси для екзистенційної тривоги
CREATE (r4:Resource {
  id: 'r_existential_book_1',
  title: 'Man\'s Search for Meaning',
  title_ua: 'Людина в пошуках сенсу',
  author: 'Viktor Frankl',
  description: 'Класична робота про знаходження сенсу в будь-яких обставинах',
  url: 'https://example.com/mans-search',
  language: 'uk',
  rating: 4.9,
  created_at: datetime()
});

CREATE (r5:Resource {
  id: 'r_existential_video_1',
  title: 'Living with Uncertainty - TED Talk',
  title_ua: 'Життя з невизначеністю',
  author: 'Speaker Name',
  description: 'Як знайти спокій у світі невизначеності',
  url: 'https://example.com/uncertainty-ted',
  language: 'en',
  duration_minutes: 18,
  created_at: datetime()
});

// Ресурси для депресивних симптомів
CREATE (r6:Resource {
  id: 'r_depression_course_1',
  title: 'Cognitive Behavioral Therapy for Depression',
  title_ua: 'Когнітивно-поведінкова терапія депресії',
  description: 'Самокерований курс на основі КПТ',
  url: 'https://example.com/cbt-course',
  language: 'uk',
  duration_minutes: 480,
  created_at: datetime()
});

CREATE (r7:Resource {
  id: 'r_depression_music_1',
  title: 'Uplifting Music Playlist',
  title_ua: 'Підбадьорливий плейлист',
  description: 'Добірка музики для покращення настрою',
  url: 'https://example.com/uplifting-playlist',
  language: 'multi',
  created_at: datetime()
});

// Ресурси для соціальної зв'язаності
CREATE (r8:Resource {
  id: 'r_social_article_1',
  title: 'Finding Your Community',
  title_ua: 'Знайти свою спільноту',
  description: 'Гайд по пошуку спільнот за інтересами',
  url: 'https://example.com/find-community',
  language: 'uk',
  created_at: datetime()
});

// Ресурси для мотивації
CREATE (r9:Resource {
  id: 'r_motivation_book_1',
  title: 'Atomic Habits',
  title_ua: 'Атомні звички',
  author: 'James Clear',
  description: 'Як будувати хороші звички та відмовлятися від поганих',
  url: 'https://example.com/atomic-habits',
  language: 'uk',
  rating: 4.7,
  created_at: datetime()
});

CREATE (r10:Resource {
  id: 'r_motivation_exercise_1',
  title: 'Daily Planning Template',
  title_ua: 'Щоденний шаблон планування',
  description: 'Структурований підхід до організації дня',
  url: 'https://example.com/planning-template',
  language: 'uk',
  created_at: datetime()
});

// Універсальні ресурси
CREATE (r11:Resource {
  id: 'r_universal_mindfulness_1',
  title: 'Introduction to Mindfulness Meditation',
  title_ua: 'Вступ до медитації усвідомленості',
  description: 'Базовий курс медитації для початківців',
  url: 'https://example.com/mindfulness-intro',
  language: 'uk',
  duration_minutes: 10,
  created_at: datetime()
});

CREATE (r12:Resource {
  id: 'r_universal_film_1',
  title: 'Inside Out',
  title_ua: 'Головоломка',
  description: 'Анімаційний фільм про емоції та їх роль у житті',
  url: 'https://example.com/inside-out',
  language: 'multi',
  rating: 4.8,
  created_at: datetime()
});

// ------------------------------------
// 7. ЗВ'ЯЗКИ: РЕСУРСИ -> ТИПИ
// ------------------------------------

MATCH (r:Resource), (rt:ResourceType)
WHERE r.id CONTAINS '_book_' AND rt.id = 'book'
CREATE (r)-[:BELONGS_TO]->(rt);

MATCH (r:Resource), (rt:ResourceType)
WHERE r.id CONTAINS '_article_' AND rt.id = 'article'
CREATE (r)-[:BELONGS_TO]->(rt);

MATCH (r:Resource), (rt:ResourceType)
WHERE r.id CONTAINS '_exercise_' AND rt.id = 'exercise'
CREATE (r)-[:BELONGS_TO]->(rt);

MATCH (r:Resource), (rt:ResourceType)
WHERE r.id CONTAINS '_video_' AND rt.id = 'video'
CREATE (r)-[:BELONGS_TO]->(rt);

MATCH (r:Resource), (rt:ResourceType)
WHERE r.id CONTAINS '_course_' AND rt.id = 'course'
CREATE (r)-[:BELONGS_TO]->(rt);

MATCH (r:Resource), (rt:ResourceType)
WHERE r.id CONTAINS '_music_' AND rt.id = 'music'
CREATE (r)-[:BELONGS_TO]->(rt);

MATCH (r:Resource), (rt:ResourceType)
WHERE r.id CONTAINS '_film_' AND rt.id = 'film'
CREATE (r)-[:BELONGS_TO]->(rt);

// ------------------------------------
// 8. ЗВ'ЯЗКИ: СТАНИ -> РЕСУРСИ
// ------------------------------------

// Висока самотність
MATCH (s:EmotionalState {id: 'loneliness_high'}), 
      (r:Resource)
WHERE r.id IN ['r_loneliness_book_1', 'r_loneliness_article_1', 
               'r_loneliness_exercise_1', 'r_social_article_1']
CREATE (r)-[:HELPS_WITH {priority: 'high', effectiveness: 0.8}]->(s);

// Помірна самотність
MATCH (s:EmotionalState {id: 'loneliness_medium'}), 
      (r:Resource)
WHERE r.id IN ['r_loneliness_article_1', 'r_social_article_1']
CREATE (r)-[:HELPS_WITH {priority: 'medium', effectiveness: 0.7}]->(s);

// Висока екзистенційна тривога
MATCH (s:EmotionalState {id: 'existential_high'}), 
      (r:Resource)
WHERE r.id IN ['r_existential_book_1', 'r_existential_video_1', 
               'r_universal_mindfulness_1']
CREATE (r)-[:HELPS_WITH {priority: 'high', effectiveness: 0.75}]->(s);

// Помірна екзистенційна тривога
MATCH (s:EmotionalState {id: 'existential_medium'}), 
      (r:Resource)
WHERE r.id IN ['r_existential_video_1', 'r_universal_mindfulness_1']
CREATE (r)-[:HELPS_WITH {priority: 'medium', effectiveness: 0.7}]->(s);

// Високі депресивні симптоми
MATCH (s:EmotionalState {id: 'depressive_high'}), 
      (r:Resource)
WHERE r.id IN ['r_depression_course_1', 'r_depression_music_1', 
               'r_universal_mindfulness_1', 'r_motivation_exercise_1']
CREATE (r)-[:HELPS_WITH {priority: 'high', effectiveness: 0.8}]->(s);

// Помірні депресивні симптоми
MATCH (s:EmotionalState {id: 'depressive_medium'}), 
      (r:Resource)
WHERE r.id IN ['r_depression_music_1', 'r_motivation_book_1', 
               'r_universal_film_1']
CREATE (r)-[:HELPS_WITH {priority: 'medium', effectiveness: 0.65}]->(s);

// Низька соціальна зв'язаність
MATCH (s:EmotionalState {id: 'social_low'}), 
      (r:Resource)
WHERE r.id IN ['r_social_article_1', 'r_loneliness_exercise_1']
CREATE (r)-[:HELPS_WITH {priority: 'high', effectiveness: 0.75}]->(s);

// Низька мотивація
MATCH (s:EmotionalState {id: 'motivation_low'}), 
      (r:Resource)
WHERE r.id IN ['r_motivation_book_1', 'r_motivation_exercise_1', 
               'r_depression_course_1']
CREATE (r)-[:HELPS_WITH {priority: 'high', effectiveness: 0.8}]->(s);

// Помірна мотивація
MATCH (s:EmotionalState {id: 'motivation_medium'}), 
      (r:Resource)
WHERE r.id IN ['r_motivation_book_1', 'r_motivation_exercise_1']
CREATE (r)-[:HELPS_WITH {priority: 'medium', effectiveness: 0.7}]->(s);

// ------------------------------------
// 9. ЗВ'ЯЗКИ: РЕСУРСИ -> ТЕМИ
// ------------------------------------

MATCH (r:Resource {id: 'r_universal_mindfulness_1'}), 
      (t:Theme {id: 'mindfulness'})
CREATE (r)-[:ADDRESSES]->(t);

MATCH (r:Resource), (t:Theme {id: 'connection'})
WHERE r.id IN ['r_loneliness_book_1', 'r_loneliness_article_1', 
               'r_loneliness_exercise_1']
CREATE (r)-[:ADDRESSES]->(t);

MATCH (r:Resource), (t:Theme {id: 'meaning'})
WHERE r.id IN ['r_existential_book_1', 'r_existential_video_1']
CREATE (r)-[:ADDRESSES]->(t);

MATCH (r:Resource {id: 'r_depression_music_1'}), 
      (t:Theme {id: 'self_compassion'})
CREATE (r)-[:ADDRESSES]->(t);

MATCH (r:Resource), (t:Theme {id: 'activation'})
WHERE r.id IN ['r_motivation_book_1', 'r_motivation_exercise_1', 
               'r_depression_course_1']
CREATE (r)-[:ADDRESSES]->(t);

MATCH (r:Resource {id: 'r_existential_video_1'}), 
      (t:Theme {id: 'acceptance'})
CREATE (r)-[:ADDRESSES]->(t);

MATCH (r:Resource {id: 'r_social_article_1'}), 
      (t:Theme {id: 'community'})
CREATE (r)-[:ADDRESSES]->(t);

MATCH (r:Resource {id: 'r_motivation_exercise_1'}), 
      (t:Theme {id: 'routine'})
CREATE (r)-[:ADDRESSES]->(t);

// ------------------------------------
// 10. ПЕРЕХРЕСНІ ЗВ'ЯЗКИ МІЖ СТАНАМИ
// ------------------------------------

// Самотність пов'язана з депресією
MATCH (s1:EmotionalState), (s2:EmotionalState)
WHERE s1.id STARTS WITH 'loneliness_' 
  AND s2.id STARTS WITH 'depressive_'
  AND s1.severity = s2.severity
CREATE (s1)-[:RELATED_TO {correlation: 0.65, type: 'comorbid'}]->(s2);

// Низька мотивація пов'язана з депресією
MATCH (s1:EmotionalState), (s2:EmotionalState)
WHERE s1.id STARTS WITH 'motivation_' 
  AND s2.id STARTS WITH 'depressive_'
  AND s1.severity = s2.severity
CREATE (s1)-[:RELATED_TO {correlation: 0.7, type: 'comorbid'}]->(s2);

// Низька соціальна зв'язаність пов'язана з самотністю
MATCH (s1:EmotionalState {id: 'social_low'}), 
      (s2:EmotionalState {id: 'loneliness_high'})
CREATE (s1)-[:RELATED_TO {correlation: 0.8, type: 'overlapping'}]->(s2);

// Екзистенційна тривога пов'язана з депресією
MATCH (s1:EmotionalState), (s2:EmotionalState)
WHERE s1.id STARTS WITH 'existential_' 
  AND s2.id STARTS WITH 'depressive