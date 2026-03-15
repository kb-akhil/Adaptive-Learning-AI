# ============================================================
# config.py - Central configuration for AgenticLearn
# ============================================================
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Database
DATABASE_URL = f"sqlite:///{BASE_DIR}/database/agenticlearn.db"

# Uploads folder
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Trained FLAN-T5 model path
TRAINED_MODEL_DIR = str(BASE_DIR / "trained_models" / "flan_t5_cn")

# API Keys


# JWT Auth
SECRET_KEY                  = os.getenv("SECRET_KEY", "agenticlearn-super-secret-key-2024")
ALGORITHM                   = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# FLAN-T5
FLAN_T5_BASE_MODEL = "google/flan-t5-base"
MAX_NEW_TOKENS     = 250
DEVICE             = "cuda"

# TF-IDF
TFIDF_TOP_N_KEYWORDS = 15