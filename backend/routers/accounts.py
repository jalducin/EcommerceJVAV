"""Endpoints de autenticación (registro, login, refresh, perfil) sobre DynamoDB."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend.deps import get_current_user
from backend.repositories import user_repo
from backend.schemas.account import (
    RefreshRequest,
    Token,
    UserCreate,
    UserLogin,
    UserPublic,
)
from backend.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _tokens_for(user_id: str) -> Token:
    return Token(
        access_token=create_access_token({"sub": user_id}),
        refresh_token=create_refresh_token({"sub": user_id}),
    )


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
def register(data: UserCreate) -> dict:
    try:
        user = user_repo.create_user(data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="El email ya está registrado"
        )
    return user_repo.public_view(user)


@router.post("/login", response_model=Token)
def login(data: UserLogin) -> Token:
    user = user_repo.get_user_by_email(str(data.email))
    if not user or not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas"
        )
    return _tokens_for(user["id"])


@router.post("/refresh", response_model=Token)
def refresh(data: RefreshRequest) -> Token:
    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh" or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido"
        )
    return _tokens_for(payload["sub"])


@router.get("/me", response_model=UserPublic)
def me(user: dict = Depends(get_current_user)) -> dict:
    return user_repo.public_view(user)
