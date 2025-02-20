import os
from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.data.database import get_db
from app.models.user import User
from app.schemas.users import TokenData, UserInDB
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля."""
    return pwd_context.hash(password)


def create_access_token(
        data: dict, expires_delta: Union[timedelta, None] = None):
    """Создание токена."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user(db: Session, username: str) -> Optional[UserInDB]:
    """Получение пользователя."""
    user = db.query(User).filter(User.username == username).first()
    if user:
        return UserInDB(
            id=user.id, username=user.username,
            hashed_password=user.hashed_password
        )
    return None


def authenticate_user(db: Session, username: str, password: str):
    """Аутентификация пользователя."""
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_all_users(skip: int, limit: int, db: Session):
    """Получение списка пользователей с пагинацией"""
    try:
        return db.query(User).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка чтения базы данных: {str(e)}"
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """Получение текущего пользователя."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невозможно проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def register_handler(user_data, db: Session):
    """Регистрация пользователя."""
    existing_user = db.query(User).filter(
        User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такое имя пользователя уже существует",
        )
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_user_handler(user_id: int, user_data, db: Session):
    """Обновление данных пользователя."""
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    for key, value in user_data.dict(exclude_unset=True).items():
        if hasattr(existing_user, key):
            setattr(existing_user, key, value)
        else:
            raise HTTPException(
                status_code=400, detail=f"Поле '{key}' не существует"
                )
    db.commit()
    db.refresh(existing_user)
    return existing_user


def delete_user_handler(user_id, db: Session):
    """Удаление пользователя."""
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    db.delete(existing_user)
    db.commit()
    return {"detail": "Пользователь успешно удалён"}
