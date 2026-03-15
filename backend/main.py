# ============================================================
# main.py — FastAPI application entry point
# ============================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db
from routes.auth          import router as auth_router
from routes.upload        import router as upload_router
from routes.assessment    import router as assessment_router
from routes.learning_path import router as learning_path_router
from routes.tutor         import router as tutor_router

app = FastAPI(
    title="AgenticLearn API",
    description="Adaptive Learning Path Generator — Multi-Agent AI System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(assessment_router)
app.include_router(learning_path_router)
app.include_router(tutor_router)


def create_dev_user():
    """Auto-create default dev account on every startup."""
    from database.db import SessionLocal
    from models.user import User
    import bcrypt
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "admin").first()
        if not existing:
            hashed = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
            user   = User(username="admin", email="admin@test.com", hashed_password=hashed)
            db.add(user)
            db.commit()
            print("[AgenticLearn] Dev user created: admin / admin123")
        else:
            print("[AgenticLearn] Dev user exists: admin / admin123")
    except Exception as e:
        print(f"[AgenticLearn] Dev user error: {e}")
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    init_db()
    create_dev_user()
    print("[AgenticLearn] Ready.")


@app.get("/")
def root():
    return {"app": "AgenticLearn", "version": "1.0.0", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "healthy"}