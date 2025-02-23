from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class Token(BaseModel):
    """Модель токена"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Данные токена"""

    username: Optional[str] = None


class UserCreate(BaseModel):
    """Создание пользователя"""

    username: str
    password: str
    email: EmailStr


class UserUpdate(BaseModel):
    """Обновление пользователя"""

    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    """Ответ API о складе"""
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """Пользователь в БД (с `hashed_password`)"""

    hashed_password: str
