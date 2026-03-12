from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_user
from ..schemas.auth import Token, TokenRefresh, UserCreate, UserLogin, UserResponse
from ..services.auth import login_user, refresh_access_token, register_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Registrar nuevo usuario cliente."""
    user = await register_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Autenticar usuario y obtener tokens JWT."""
    return await login_user(db, credentials.email, credentials.password)


@router.post("/refresh", response_model=Token)
async def refresh(data: TokenRefresh):
    """Renovar access token usando refresh token."""
    return refresh_access_token(data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtener perfil del usuario autenticado."""
    from sqlalchemy import select

    from ..models.user import User

    result = await db.execute(select(User).where(User.id == int(current_user["sub"])))
    user = result.scalar_one_or_none()
    if not user:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
