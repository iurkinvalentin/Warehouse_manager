import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status
from app.services.user_service import (
    verify_password, get_password_hash, create_access_token,
    get_user, authenticate_user, get_current_user,
    register_handler, delete_user_handler
)
from app.models.user import User
from app.schemas.users import UserInDB, TokenData, UserCreate
from app.data.database import get_db


SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@pytest.fixture
def mock_db():
    """Создает мокнутую сессию SQLAlchemy"""
    return MagicMock()


@pytest.fixture
def test_user():
    """Создает тестового пользователя"""
    return User(id=1, username="testuser", hashed_password=get_password_hash("password123"))


def test_get_password_hash():
    """Проверка хеширования пароля"""
    hashed_password = get_password_hash("password123")
    assert hashed_password != "password123"
    assert isinstance(hashed_password, str)


def test_verify_password():
    """Проверка сравнения пароля"""
    hashed_password = get_password_hash("password123")
    assert verify_password("password123", hashed_password) is True
    assert verify_password("wrongpassword", hashed_password) is False


def test_create_access_token():
    """Генерация токена"""
    data = {"sub": "testuser"}
    token = create_access_token(data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    assert isinstance(token, str)
    
    decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_data["sub"] == "testuser"
    assert "exp" in decoded_data


def test_get_user_found(mock_db, test_user):
    """Получение пользователя (найден)"""
    mock_db.query().filter().first.return_value = test_user

    result = get_user(mock_db, "testuser")

    assert result.username == "testuser"
    mock_db.query().filter().first.assert_called_once()


def test_get_user_not_found(mock_db):
    """Ошибка: Пользователь не найден"""
    mock_db.query().filter().first.return_value = None

    result = get_user(mock_db, "unknownuser")

    assert result is None


def test_authenticate_user_success(mock_db, test_user):
    """Аутентификация успешна"""
    mock_db.query().filter().first.return_value = test_user

    result = authenticate_user(mock_db, "testuser", "password123")

    assert result.username == "testuser"


def test_authenticate_user_wrong_password(mock_db, test_user):
    """Ошибка: Неверный пароль"""
    mock_db.query().filter().first.return_value = test_user

    result = authenticate_user(mock_db, "testuser", "wrongpassword")

    assert result is False


def test_authenticate_user_not_found(mock_db):
    """Ошибка: Пользователь не найден"""
    mock_db.query().filter().first.return_value = None

    result = authenticate_user(mock_db, "unknownuser", "password123")

    assert result is False


@pytest.mark.asyncio
@patch("app.services.user_service.jwt.decode")
async def test_get_current_user_success(mock_jwt_decode, mock_db, test_user):
    """Успешное получение текущего пользователя по токену"""
    mock_jwt_decode.return_value = {"sub": "testuser"}
    mock_db.query().filter().first.return_value = test_user

    result = await get_current_user("fake_token", mock_db)

    assert result.username == "testuser"


@pytest.mark.asyncio
@patch("app.services.user_service.jwt.decode", side_effect=JWTError)
async def test_get_current_user_invalid_token(mock_jwt_decode, mock_db):
    """Ошибка: Невалидный токен"""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("invalid_token", mock_db)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Невозможно проверить учетные данные" in exc_info.value.detail


def test_register_handler_success(mock_db):
    """Успешная регистрация пользователя"""
    user_data = UserCreate(username="newuser", password="password123")
    mock_db.query().filter().first.return_value = None  # Пользователя нет

    result = register_handler(user_data, mock_db)

    assert result.username == "newuser"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_register_handler_user_already_exists(mock_db):
    """Ошибка: Пользователь уже существует"""
    user_data = UserCreate(username="existinguser", password="password123")
    mock_db.query().filter().first.return_value = User(id=1, username="existinguser")

    with pytest.raises(HTTPException) as exc_info:
        register_handler(user_data, mock_db)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Пользователь с таким именем уже существует" in exc_info.value.detail


def test_delete_user_handler_success(mock_db, test_user):
    """Успешное удаление пользователя"""
    mock_db.query().filter().first.return_value = test_user

    result = delete_user_handler(1, mock_db)

    assert result["detail"] == "Пользователь успешно удалён"
    mock_db.delete.assert_called_once_with(test_user)
    mock_db.commit.assert_called_once()


def test_delete_user_handler_not_found(mock_db):
    """Ошибка: Удаление несуществующего пользователя"""
    mock_db.query().filter().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_user_handler(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Пользователь не найден" in exc_info.value.detail
