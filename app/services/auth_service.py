import hashlib
import hmac
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserLogin, UserSignup

PBKDF2_ITERATIONS = 120_000


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${hashed}"


def _verify_password(password: str, encoded_password: str) -> bool:
    try:
        algorithm, iterations, salt, stored_hash = encoded_password.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        computed_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        ).hex()
        return hmac.compare_digest(computed_hash, stored_hash)
    except (ValueError, TypeError):
        return False


def signup_user(db: Session, payload: UserSignup) -> User:
    existing_user = db.scalar(select(User).where(User.email == str(payload.email).lower().strip()))
    if existing_user:
        raise ValueError("An account with this email already exists.")

    user = User(
        full_name=payload.full_name.strip(),
        email=str(payload.email).lower().strip(),
        hashed_password=_hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, payload: UserLogin) -> User:
    user = db.scalar(select(User).where(User.email == str(payload.email).lower().strip()))
    if not user or not _verify_password(payload.password, user.hashed_password):
        raise LookupError("Invalid email or password.")
    return user
