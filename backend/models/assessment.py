# ============================================================
# models/assessment.py
# ============================================================
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"),    nullable=False)
    syllabus_id   = Column(Integer, ForeignKey("syllabi.id"),  nullable=False)
    questions_json = Column(Text,   nullable=False)   # JSON list of question dicts
    created_at    = Column(DateTime, default=datetime.utcnow)
    is_completed  = Column(Boolean,  default=False)

    student  = relationship("User",     back_populates="assessments")
    syllabus = relationship("Syllabus", back_populates="assessments")
    result   = relationship("AssessmentResult", back_populates="assessment", uselist=False)


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id                 = Column(Integer, primary_key=True, index=True)
    assessment_id      = Column(Integer, ForeignKey("assessments.id"), nullable=False, unique=True)
    user_id            = Column(Integer, ForeignKey("users.id"),       nullable=False)
    answers_json       = Column(Text,  nullable=False)
    weak_topics        = Column(Text,  nullable=True)   # JSON list
    strong_topics      = Column(Text,  nullable=True)   # JSON list
    accuracy           = Column(Float, nullable=True)   # 0.0 – 100.0
    learning_path_json = Column(Text,  nullable=True)   # JSON learning path
    submitted_at       = Column(DateTime, default=datetime.utcnow)

    assessment = relationship("Assessment", back_populates="result")