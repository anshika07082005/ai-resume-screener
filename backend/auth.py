import os
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from typing import Optional

import bcrypt

from dotenv import load_dotenv

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from jose import (
    ExpiredSignatureError,
    JWTError,
    jwt,
)

from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    tags=["Authentication"],
)


# ============================================================
# JWT CONFIGURATION
# ============================================================

SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "fallback-development-secret-change-me",
)

ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256",
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "1440",
    )
)


security = HTTPBearer(
    auto_error=False,
)


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(
    password: str,
) -> str:

    password_bytes = password.encode(
        "utf-8"
    )

    hashed_password = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )

    return hashed_password.decode(
        "utf-8"
    )


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:

    try:

        return bcrypt.checkpw(
            plain_password.encode(
                "utf-8"
            ),
            hashed_password.encode(
                "utf-8"
            ),
        )

    except Exception:

        return False


# ============================================================
# CREATE JWT
# ============================================================

def create_access_token(
    user_id: int,
    email: str,
) -> str:

    now = datetime.now(
        timezone.utc
    )

    expiration = (
        now
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": int(
            now.timestamp()
        ),
        "exp": int(
            expiration.timestamp()
        ),
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return token


# ============================================================
# DECODE JWT
# ============================================================

def decode_access_token(
    token: str,
) -> Optional[dict]:

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[
                ALGORITHM
            ],
        )

        return payload

    except ExpiredSignatureError:

        return None

    except JWTError:

        return None

    except Exception:

        return None


# ============================================================
# CURRENT USER
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    db: Session = Depends(
        get_db
    ),
) -> User:

    if credentials is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    token = credentials.credentials

    if not token:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing",
        )

    payload = decode_access_token(
        token
    )

    if payload is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get(
        "sub"
    )

    if user_id is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    try:

        user_id = int(
            user_id
        )

    except (
        ValueError,
        TypeError,
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register"
)
def register_user(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(
        get_db
    ),
):

    normalized_email = (
        email
        .strip()
        .lower()
    )

    if not normalized_email:

        raise HTTPException(
            status_code=400,
            detail="Email is required",
        )

    if len(password) < 6:

        raise HTTPException(
            status_code=400,
            detail=(
                "Password must contain "
                "at least 6 characters"
            ),
        )

    existing_user = (
        db.query(User)
        .filter(
            User.email
            == normalized_email
        )
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )

    user = User(
        email=normalized_email,
        password=hash_password(
            password
        ),
    )

    db.add(
        user
    )

    db.commit()

    db.refresh(
        user
    )

    return {
        "message":
            "User registered successfully",

        "user_id":
            user.id,

        "email":
            user.email,
    }


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login"
)
def login_user(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(
        get_db
    ),
):

    normalized_email = (
        email
        .strip()
        .lower()
    )

    user = (
        db.query(User)
        .filter(
            User.email
            == normalized_email
        )
        .first()
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    password_valid = verify_password(
        password,
        user.password,
    )

    if not password_valid:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
    )

    return {
        "access_token":
            access_token,

        "token_type":
            "bearer",

        "expires_in":
            ACCESS_TOKEN_EXPIRE_MINUTES
            * 60,

        "user": {
            "id":
                user.id,

            "email":
                user.email,
        },
    }


# ============================================================
# CURRENT USER ENDPOINT
# ============================================================

@router.get(
    "/me"
)
def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):

    return {
        "id":
            current_user.id,

        "email":
            current_user.email,

        "authenticated":
            True,
    }