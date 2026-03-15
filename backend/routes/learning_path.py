# ============================================================
# routes/learning_path.py — Retrieve learning path
# ============================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db
from models.assessment import Assessment, AssessmentResult
from models.user import User
from routes.auth import get_current_user

router = APIRouter(prefix="/learning-path", tags=["Learning Path"])


@router.get("/latest/me")
def get_latest_path(db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    result = (
        db.query(AssessmentResult)
        .filter(AssessmentResult.user_id == current_user.id)
        .order_by(AssessmentResult.submitted_at.desc())
        .first()
    )
    if not result:
        raise HTTPException(404, "No learning path found. Complete an assessment first.")
    return {
        "assessment_id": result.assessment_id,
        "accuracy":      result.accuracy,
        "weak_topics":   json.loads(result.weak_topics   or "[]"),
        "strong_topics": json.loads(result.strong_topics or "[]"),
        "learning_path": json.loads(result.learning_path_json or "{}"),
        "submitted_at":  result.submitted_at.isoformat()
    }


@router.get("/{assessment_id}")
def get_learning_path(
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
    if not assessment.result:
        raise HTTPException(400, "Assessment not yet completed.")
    r = assessment.result
    return {
        "assessment_id": assessment_id,
        "accuracy":      r.accuracy,
        "weak_topics":   json.loads(r.weak_topics   or "[]"),
        "strong_topics": json.loads(r.strong_topics or "[]"),
        "learning_path": json.loads(r.learning_path_json or "{}")
    }