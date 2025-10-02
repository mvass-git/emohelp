def generate_results(test_id, answers):
    # Дуже проста логіка для MVP
    # Пізніше тут може бути обробка балів, алгоритми тощо
    score = len([a for a in answers if a])  # умовний підрахунок
    if score < 3:
        mood = "Вам може бути важко, радимо спробувати релаксаційні практики."
    else:
        mood = "Ваш стан відносно стабільний, але не забувайте про підтримку."

    return {
        "test_id": test_id,
        "score": score,
        "summary": mood,
        "materials": [
            {"title": "Дихальні практики", "link": "/materials/breathing"},
            {"title": "Коротка медитація", "link": "/materials/meditation"}
        ]
    }
