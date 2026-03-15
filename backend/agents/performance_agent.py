# ============================================================
# agents/performance_agent.py — Performance Analysis Agent
# Fully subject-independent: pure math on answers vs correct keys
# ============================================================

def analyze_performance(questions: list, student_answers: dict) -> dict:
    """
    Analyze student answers against correct answers.
    Works for any subject — purely compares answer keys.

    Args:
        questions:       List of question dicts with 'answer' key
        student_answers: {str(question_id): selected_answer_key}

    Returns:
        {accuracy, weak_topics, strong_topics, topic_scores,
         total_correct, total_questions, per_question}
    """
    if not questions:
        return _empty()

    topic_stats  = {}   # {topic: {correct: int, total: int}}
    per_question = []
    total_correct = 0

    for q in questions:
        qid            = str(q["id"])
        topic          = q.get("topic", "General")
        correct_answer = q.get("answer", "")
        student_answer = student_answers.get(qid, "").strip()

        is_correct = student_answer.upper() == correct_answer.upper()
        if is_correct:
            total_correct += 1

        if topic not in topic_stats:
            topic_stats[topic] = {"correct": 0, "total": 0}
        topic_stats[topic]["total"] += 1
        if is_correct:
            topic_stats[topic]["correct"] += 1

        per_question.append({
            "id":             q["id"],
            "topic":          topic,
            "correct":        is_correct,
            "student_answer": student_answer,
            "correct_answer": correct_answer
        })

    total_questions = len(questions)
    accuracy = round((total_correct / total_questions) * 100, 2) if total_questions else 0.0

    # Classify: weak < 60%, strong >= 70%
    topic_scores = {}
    weak_topics  = []
    strong_topics = []

    for topic, stats in topic_stats.items():
        pct = round((stats["correct"] / stats["total"]) * 100, 2) if stats["total"] else 0.0
        topic_scores[topic] = {
            "correct": stats["correct"],
            "total":   stats["total"],
            "pct":     pct
        }
        if pct < 60.0:
            weak_topics.append(topic)
        elif pct >= 70.0:
            strong_topics.append(topic)

    # Sort: weakest first (highest priority in learning path)
    weak_topics.sort(key=lambda t: topic_scores[t]["pct"])
    strong_topics.sort(key=lambda t: topic_scores[t]["pct"], reverse=True)

    print(f"[PerformanceAgent] Accuracy:{accuracy}% "
          f"Weak:{weak_topics} Strong:{strong_topics}")

    return {
        "accuracy":        accuracy,
        "weak_topics":     weak_topics,
        "strong_topics":   strong_topics,
        "topic_scores":    topic_scores,
        "total_correct":   total_correct,
        "total_questions": total_questions,
        "per_question":    per_question
    }


def _empty() -> dict:
    return {
        "accuracy": 0.0, "weak_topics": [], "strong_topics": [],
        "topic_scores": {}, "total_correct": 0,
        "total_questions": 0, "per_question": []
    }