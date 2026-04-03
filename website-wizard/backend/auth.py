from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.models.user import User
from backend.schemas import UserCreate, UserLogin, UserOut, TokenOut
from backend.security import (
    hash_password,
    verify_password,
    create_access_token,
    JWT_SECRET,
    ALGORITHM,
)

router = APIRouter(prefix="/auth", tags=["auth"])

# This enables the 🔒 Authorize button in Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# =========================
# DB Dependency
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# Get Current User (JWT Protected)
# =========================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        raise credentials_exception

    return user


# =========================
# Register
# =========================
@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def register(data: UserCreate, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# =========================
# Login (JSON Body)
# =========================
@router.post("/login", response_model=TokenOut)
def login(data: UserLogin, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(subject=str(user.id))

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# =========================
# Protected Route
# =========================
@router.get(
    "/me",
    response_model=UserOut,
)
def read_current_user(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),  # 👈 THIS LINE FOR SWAGGER
):
    return current_user