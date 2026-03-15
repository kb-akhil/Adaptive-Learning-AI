# ============================================================
# routes/upload.py — Syllabus PDF upload (fully generic)
# ============================================================
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import shutil, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db
from models.syllabus import Syllabus
from models.user import User
from routes.auth import get_current_user
from services.pdf_extractor import extract_text_from_pdf
from services.keyword_extractor import (
    extract_keywords, extract_hierarchy,
    keywords_to_json, hierarchy_to_json
)
from config import UPLOAD_DIR

router = APIRouter(prefix="/upload", tags=["Syllabus Upload"])


@router.post("/syllabus")
async def upload_syllabus(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted.")

    save_path = UPLOAD_DIR / f"user_{current_user.id}_{file.filename}"
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        text = extract_text_from_pdf(str(save_path))
        if not text or len(text.strip()) < 50:
            raise HTTPException(400,
                "Cannot extract text. Ensure PDF is not scanned/image-only.")

        # Extract flat keywords for assessment question generation
        keywords  = extract_keywords(text, top_n=15)

        # Extract hierarchy for learning path subtopics
        hierarchy = extract_hierarchy(text, top_n=15)

        if not keywords:
            raise HTTPException(400, "No topics extracted. Upload a text-based syllabus PDF.")

        # Subject label — taken from filename, no hardcoding
        subject = os.path.splitext(file.filename)[0].replace("_", " ").title()

        syllabus = Syllabus(
            user_id=current_user.id,
            filename=file.filename,
            keywords=keywords_to_json(keywords),
            subject=subject,
            # Store hierarchy after separator in extracted_text
            extracted_text=text[:8000] + "\n\n__HIERARCHY__\n" + hierarchy_to_json(hierarchy)
        )
        db.add(syllabus); db.commit(); db.refresh(syllabus)

        return {
            "syllabus_id": syllabus.id,
            "filename":    file.filename,
            "subject":     subject,
            "topics":      keywords,
            "topic_count": len(keywords),
            "message":     f"Syllabus processed. {len(keywords)} topics extracted."
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Processing error: {str(e)}")


@router.get("/syllabi")
def get_user_syllabi(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rows = db.query(Syllabus).filter(Syllabus.user_id == current_user.id).all()
    return [
        {
            "id":          s.id,
            "filename":    s.filename,
            "subject":     s.subject,
            "uploaded_at": s.uploaded_at.isoformat()
        }
        for s in rows
    ]