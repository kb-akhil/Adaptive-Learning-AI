# ============================================================
# routes/assessment.py
# ============================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db
from models.assessment import Assessment, AssessmentResult
from models.syllabus import Syllabus
from models.user import User
from routes.auth import get_current_user
from agents.question_agent import generate_questions_for_topics
from agents.performance_agent import analyze_performance
from agents.path_agent import generate_learning_path
from services.keyword_extractor import json_to_keywords, json_to_hierarchy

router = APIRouter(prefix="/assessment", tags=["Assessment"])


class SubmitAnswersRequest(BaseModel):
    assessment_id: int
    answers:       dict


def _get_hierarchy(syllabus: Syllabus) -> list:
    if not syllabus or not syllabus.extracted_text:
        return []
    if "__HIERARCHY__" in syllabus.extracted_text:
        parts = syllabus.extracted_text.split("__HIERARCHY__")
        if len(parts) > 1:
            return json_to_hierarchy(parts[1].strip())
    return []


def _get_assessment_topics(syllabus: Syllabus) -> list:
    hierarchy = _get_hierarchy(syllabus)

    if hierarchy:
        if len(hierarchy) >= 3:
            # Multiple units — test on unit titles
            topics = [u["title"] for u in hierarchy if u.get("title")]
            print(f"[Assessment] Multi-unit mode: {topics}")
        else:
            # Single/few units — test on subtopics
            topics = []
            for unit in hierarchy:
                for sub in unit.get("subtopics", []):
                    if sub not in topics:
                        topics.append(sub)
            print(f"[Assessment] Single-unit mode subtopics: {topics}")

        return topics[:8]

    # Fallback
    return json_to_keywords(syllabus.keywords or "[]")[:8]


def _get_all_topics_for_path(syllabus: Syllabus, assessed_topics: list) -> list:
    """
    Get complete topic list for learning path generation.
    These become the modules — must cover everything in syllabus.
    """
    hierarchy = _get_hierarchy(syllabus)

    if hierarchy:
        if len(hierarchy) >= 3:
            # Full syllabus — modules = unit titles
            return [u["title"] for u in hierarchy]
        else:
            # Single unit — modules = subtopics
            topics = []
            for unit in hierarchy:
                for sub in unit.get("subtopics", []):
                    if sub not in topics:
                        topics.append(sub)
            return topics

    return assessed_topics


@router.get("/generate/{syllabus_id}")
def generate_assessment(
    syllabus_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    syllabus = db.query(Syllabus).filter(
        Syllabus.id == syllabus_id,
        Syllabus.user_id == current_user.id
    ).first()
    if not syllabus:
        raise HTTPException(404, "Syllabus not found.")

    topics = _get_assessment_topics(syllabus)
    if not topics:
        raise HTTPException(400, "No topics found in syllabus.")

    questions = generate_questions_for_topics(topics, questions_per_topic=2)
    if not questions:
        raise HTTPException(500, "Question generation failed.")

    assessment = Assessment(
        user_id=current_user.id,
        syllabus_id=syllabus_id,
        questions_json=json.dumps(questions)
    )
    db.add(assessment); db.commit(); db.refresh(assessment)

    return {
        "assessment_id":  assessment.id,
        "syllabus_id":    syllabus_id,
        "topic_count":    len(topics),
        "question_count": len(questions),
        "questions":      questions,
        "message":        f"Assessment generated: {len(questions)} questions."
    }


@router.post("/submit")
def submit_assessment(
    req: SubmitAnswersRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assessment = db.query(Assessment).filter(
        Assessment.id == req.assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    if not assessment:
        raise HTTPException(404, "Assessment not found.")

    if assessment.is_completed and assessment.result:
        r = assessment.result
        return {
            "message":       "Already submitted.",
            "accuracy":      r.accuracy,
            "weak_topics":   json.loads(r.weak_topics   or "[]"),
            "strong_topics": json.loads(r.strong_topics or "[]"),
            "learning_path": json.loads(r.learning_path_json or "{}")
        }

    questions   = json.loads(assessment.questions_json)
    performance = analyze_performance(questions, req.answers)

    syllabus    = db.query(Syllabus).filter(Syllabus.id == assessment.syllabus_id).first()
    hierarchy   = _get_hierarchy(syllabus)

    # Get full topic list for path — covers all topics in syllabus
    all_topics = _get_all_topics_for_path(syllabus, performance["weak_topics"] + performance["strong_topics"])

    print(f"[Assessment] Weak: {performance['weak_topics']}")
    print(f"[Assessment] Strong: {performance['strong_topics']}")
    print(f"[Assessment] All topics for path: {all_topics}")

    learning_path = generate_learning_path(
        weak_topics=performance["weak_topics"],
        strong_topics=performance["strong_topics"],
        all_topics=all_topics,
        accuracy=performance["accuracy"],
        hierarchy=hierarchy,
    )

    result = AssessmentResult(
        assessment_id=assessment.id,
        user_id=current_user.id,
        answers_json=json.dumps(req.answers),
        weak_topics=json.dumps(performance["weak_topics"]),
        strong_topics=json.dumps(performance["strong_topics"]),
        accuracy=performance["accuracy"],
        learning_path_json=json.dumps(learning_path)
    )
    assessment.is_completed = True
    db.add(result); db.commit()

    return {
        "message":         "Assessment submitted.",
        "accuracy":        performance["accuracy"],
        "total_correct":   performance["total_correct"],
        "total_questions": performance["total_questions"],
        "weak_topics":     performance["weak_topics"],
        "strong_topics":   performance["strong_topics"],
        "topic_scores":    performance["topic_scores"],
        "per_question":    performance["per_question"],
        "learning_path":   learning_path
    }


@router.get("/result/{assessment_id}")
def get_result(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    if not assessment:
        raise HTTPException(404, "Assessment not found.")
    if not assessment.is_completed or not assessment.result:
        raise HTTPException(400, "Assessment not yet submitted.")
    r = assessment.result
    return {
        "accuracy":      r.accuracy,
        "weak_topics":   json.loads(r.weak_topics   or "[]"),
        "strong_topics": json.loads(r.strong_topics or "[]"),
        "learning_path": json.loads(r.learning_path_json or "{}"),
        "submitted_at":  r.submitted_at.isoformat()
    }