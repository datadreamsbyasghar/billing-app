from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models import User
from schemas import LoginInput, RegisterInput, TokenResponse
from database import get_db
from security import get_password_hash, verify_password, create_access_token, get_current_user, ensure_admin

router = APIRouter()

@router.post("/auth/login", response_model=TokenResponse)
def login(input: LoginInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == input.username).first()
    if not user or not verify_password(input.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    return TokenResponse(access_token=token, token_type="bearer", role=user.role)  # ✅ now matches schema

@router.post("/auth/register")
def register(input: RegisterInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_admin(current_user)
    existing = db.query(User).filter(User.username == input.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_pw = get_password_hash(input.password)
    role = input.role if input.role in ("admin", "staff") else "staff"
    user = User(username=input.username, hashed_password=hashed_pw, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered successfully", "username": user.username, "role": user.role}