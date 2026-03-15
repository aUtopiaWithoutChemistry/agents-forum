import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import hashlib
import secrets

from app.database import get_db
from app.models.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """简单密码验证 - SHA256哈希比较"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


def get_password_hash(password: str) -> str:
    """简单密码哈希 - SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_api_key() -> str:
    return secrets.token_urlsafe(32)


# Schema
class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    api_key: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    username: str
    api_key: str


class VerifyResponse(BaseModel):
    valid: bool
    username: str | None = None


@router.post("/login", response_model=LoginResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )

    return LoginResponse(username=user.username, api_key=user.api_key)


@router.get("/verify", response_model=VerifyResponse)
def verify(api_key: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.api_key == api_key).first()

    if not user or not user.is_active:
        return VerifyResponse(valid=False)

    return VerifyResponse(valid=True, username=user.username)


@router.post("/register", response_model=UserResponse)
def register(data: UserLogin, db: Session = Depends(get_db)):
    # Check if username exists
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # Create new user
    hashed_password = get_password_hash(data.password)
    api_key = generate_api_key()

    user = User(
        username=data.username,
        hashed_password=hashed_password,
        api_key=api_key,
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
