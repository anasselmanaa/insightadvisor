from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend_core.database import get_db
from backend_core.auth_service import (
    create_user,
    authenticate_user,
    create_access_token,
    get_current_user,
)

router = APIRouter(tags=["Auth"])


class RegisterRequest(BaseModel):
    email:    str
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str
    username:     str
    email:        str


# ── /auth/register ────────────────────────────────────
@router.post("/auth/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    user = create_user(db, body.email, body.username, body.password)
    return {
        "status":   "success",
        "message":  "Account created successfully",
        "email":    user.email,
        "username": user.username,
    }


# ── /auth/login ───────────────────────────────────────
@router.post("/auth/login", response_model=TokenResponse)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db:   Session = Depends(get_db),
):
    user  = authenticate_user(db, form.username, form.password)
    token = create_access_token({"sub": user.email})
    return {
        "access_token": token,
        "token_type":   "bearer",
        "username":     user.username,
        "email":        user.email,
    }


# ── /auth/me ──────────────────────────────────────────
@router.get("/auth/me")
def me(current_user=Depends(get_current_user)):
    return {
        "email":    current_user.email,
        "username": current_user.username,
    }