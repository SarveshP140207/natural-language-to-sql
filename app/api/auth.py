from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_current_user
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.database.app_connection import AppSessionLocal
from app.database.models import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(request: RegisterRequest):
    db = AppSessionLocal()

    try:
        existing_user = db.scalar(
            select(User).where(
                (User.username == request.username)
                | (User.email == request.email)
            )
        )

        if existing_user:
            if existing_user.username == request.username:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already exists.",
                )

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists.",
            )

        user = User(
            username=request.username,
            email=request.email,
            password_hash=hash_password(request.password),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return UserResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
        )

    finally:
        db.close()


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login_user(request: LoginRequest):
    db = AppSessionLocal()

    try:
        user = db.scalar(
            select(User).where(
                User.username == request.username
            )
        )

        if not user or not verify_password(
            request.password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )

        access_token = create_access_token(
            user_id=user.user_id,
            username=user.username,
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                is_active=user.is_active,
            ),
        )

    finally:
        db.close()


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return UserResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
    )