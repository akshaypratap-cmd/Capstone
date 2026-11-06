from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.dependencies import get_db, get_current_user
from app import crud

from app.models import User

from app.schemas import (
    UserCreate,
    UserResponse,
    TokenResponse
)

from app.security import (
    hash_password,
    verify_password,
    create_access_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# Register user
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    email = str(user.email).lower()

    existing_user = crud.get_user_by_email(
        db,
        email
    )

    if existing_user:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    hashed_password = hash_password(user.password)

    try:

        new_user = crud.create_user(
            db,
            email,
            hashed_password
        )

        return new_user

    except IntegrityError:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )


# Login user
@router.post(
    "/login",
    response_model=TokenResponse
)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    email = form_data.username.strip().lower()

    user = crud.get_user_by_email(
        db,
        email
    )

    if not user or not verify_password(
        form_data.password,
        user.hashed_password
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(user.id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )


# Get logged-in user's information
@router.get(
    "/me",
    response_model=UserResponse
)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):

    return current_user