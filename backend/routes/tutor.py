# ============================================================
# routes/tutor.py
# ============================================================
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db
from models.user import User
from routes.auth import get_current_user
from agents.tutor_agent import ask_tutor

router = APIRouter(prefix="/tutor", tags=["Tutor"])


class HistoryMessage(BaseModel):
    role: str   # "user" or "assistant"
    text: str


class TutorRequest(BaseModel):
    question: str
    topic:    str = ""
    history:  Optional[List[HistoryMessage]] = []


@router.post("/ask")
def ask_tutor_endpoint(
    req: TutorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not req.question.strip():
        return {"answer": "Please type a question."}

    history = [{"role": h.role, "text": h.text} for h in (req.history or [])]

    result = ask_tutor(
        question=req.question.strip(),
        context_topic=req.topic.strip(),
        history=history
    )
    return {
        "question": req.question,
        "answer":   result["answer"],
        "topic":    req.topic,
        "source":   result.get("source", ""),
    }