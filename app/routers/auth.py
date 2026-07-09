from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status as http_status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.security import create_access_token, get_password_hash, verify_password
from app.database import get_db
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserOut
from app.settings import settings


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/register",
    response_model=UserOut,
    status_code=http_status.HTTP_201_CREATED,
)
def register_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = db.scalar(
        select(User).where(User.email == payload.email.lower())
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    user_count = db.scalar(select(func.count()).select_from(User)) or 0
    role = "admin" if user_count == 0 else "tech"

    user = User(
        email=payload.email.lower(),
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name.strip(),
        role=role,
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        ) from None

    db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=Token,
)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(User.email == form_data.username.lower())
    )

    if user is None or not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes
    )

    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires,
        additional_claims={"role": user.role},
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get(
    "/me",
    response_model=UserOut,
)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user
