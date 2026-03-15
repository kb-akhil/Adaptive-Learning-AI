# ============================================================
# services/pdf_extractor.py - PDF text extraction (PyMuPDF)
# Subject-independent: extracts text from any PDF
# ============================================================
import fitz   # PyMuPDF
import re
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF and return cleaned plain text."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages = []
    with fitz.open(str(pdf_path)) as doc:
        print(f"[PDF] Extracting {doc.page_count} pages: {pdf_path.name}")
        for page in doc:
            text = page.get_text("text")
            if text.strip():
                pages.append(text)

    return _clean("\n".join(pages))


def _clean(text: str) -> str:
    text = re.sub(r'[^\x20-\x7E\n]', ' ', text)   # remove non-ASCII
    text = re.sub(r'\n{3,}', '\n\n', text)          # max 2 blank lines
    text = re.sub(r' {2,}', ' ', text)              # max 1 space
    return text.strip()


def extract_headings_from_text(text: str) -> list:
    """
    Heuristic heading extraction — subject-independent.
    Catches numbered items, bullets, and ALL-CAPS lines.
    """
    topics = []
    for line in text.split('\n'):
        line = line.strip()
        if not line or len(line) < 3:
            continue

        # Numbered: "1. Topic", "Unit 1: Topic", "Chapter 2 - Topic"
        if re.match(r'^(\d+[\.\)]\s+|Unit\s+\d+|Chapter\s+\d+)', line, re.IGNORECASE):
            topic = re.sub(r'^[\d\.\)\s]+|^(Unit|Chapter)\s+\d+[\:\.\-]?\s*',
                           '', line, flags=re.IGNORECASE).strip()
            if topic:
                topics.append(topic)

        # Bullets
        elif re.match(r'^[•\-\*]\s+', line):
            topic = re.sub(r'^[•\-\*]\s+', '', line).strip()
            if len(topic) > 5:
                topics.append(topic)

        # ALL CAPS headings
        elif line.isupper() and 5 < len(line) < 80:
            topics.append(line.title())

    # Deduplicate, preserve order
    seen, unique = set(), []
    for t in topics:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique.append(t)
    return unique[:30]