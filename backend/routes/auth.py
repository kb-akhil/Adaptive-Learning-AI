# ============================================================
# routes/auth.py — Register, Login, JWT
# ============================================================
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db
from models.user import User
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router        = APIRouter(prefix="/auth", tags=["Authentication"])
pwd_context   = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class RegisterRequest(BaseModel):
    username: str
    email:    str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str
    username:     str
    user_id:      int


def hash_password(p: str)          -> str:  return pwd_context.hash(p)
def verify_password(p: str, h: str)-> bool: return pwd_context.verify(p, h)


def create_access_token(data: dict) -> str:
    payload = {**data, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)) -> User:
    exc = HTTPException(status_code=401, detail="Invalid or expired token",
                        headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid: int = payload.get("user_id")
        if uid is None: raise exc
    except JWTError:
        raise exc
    user = db.query(User).filter(User.id == uid).first()
    if not user: raise exc
    return user


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(400, "Username already exists")
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(username=req.username, email=req.email,
                hashed_password=hash_password(req.password))
    db.add(user); db.commit(); db.refresh(user)
    token = create_access_token({"user_id": user.id, "username": user.username})
    return TokenResponse(access_token=token, token_type="bearer",
                         username=user.username, user_id=user.id)


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Invalid username or password")
    token = create_access_token({"user_id": user.id, "username": user.username})
    return TokenResponse(access_token=token, token_type="bearer",
                         username=user.username, user_id=user.id)


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id, "username": current_user.username,
            "email": current_user.email}