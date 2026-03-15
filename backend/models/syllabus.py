# ============================================================
# models/syllabus.py
# ============================================================
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import Base


class Syllabus(Base):
    __tablename__ = "syllabi"

    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename       = Column(String, nullable=False)
    extracted_text = Column(Text,   nullable=True)   # Full text from PDF
    keywords       = Column(Text,   nullable=True)   # JSON list of topics
    subject        = Column(String, nullable=True)   # Detected subject label (display only)
    uploaded_at    = Column(DateTime, default=datetime.utcnow)

    owner       = relationship("User",       back_populates="syllabi")
    assessments = relationship("Assessment", back_populates="syllabus")