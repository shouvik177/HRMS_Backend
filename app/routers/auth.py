from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AuthResponse, UserLogin, UserRead, UserSignup
from app.services.auth_service import login_user, signup_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup_endpoint(payload: UserSignup, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        user = signup_user(db=db, payload=payload)
        return AuthResponse(message="Signup successful.", user=UserRead.model_validate(user))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account.",
        ) from exc


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def login_endpoint(payload: UserLogin, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        user = login_user(db=db, payload=payload)
        return AuthResponse(message="Login successful.", user=UserRead.model_validate(user))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to login.",
        ) from exc
