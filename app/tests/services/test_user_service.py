from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.models.user import User
from app.schemas.users import UserCreate
from app.services.user_service import (
    authenticate_user,
    create_access_token,
    delete_user_handler,
    get_current_user,
    get_password_hash,
    get_user,
    register_handler,
    verify_password,
)

SECRET_KEY = "default-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def test_user():
    return User(
        id=1, username="testuser", hashed_password=get_password_hash(
            "password123"))


def test_get_password_hash():
    hashed_password = get_password_hash("password123")
    assert hashed_password != "password123"
    assert isinstance(hashed_password, str)


def test_verify_password():
    hashed_password = get_password_hash("password123")
    assert verify_password("password123", hashed_password) is True
    assert verify_password("wrongpassword", hashed_password) is False


def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(
        data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    assert isinstance(token, str)

    decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_data["sub"] == "testuser"
    assert "exp" in decoded_data


def test_get_user_found(mock_db, test_user):
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = test_user
    mock_db.query.return_value = mock_query

    result = get_user(mock_db, "testuser")

    assert result.username == "testuser"
    mock_query.first.assert_called_once()


def test_get_user_not_found(mock_db):
    mock_db.query().filter().first.return_value = None

    result = get_user(mock_db, "unknownuser")

    assert result is None


def test_authenticate_user_success(mock_db, test_user):
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = test_user
    mock_db.query.return_value = mock_query

    result = authenticate_user(mock_db, "testuser", "password123")

    assert result.username == "testuser"


def test_authenticate_user_wrong_password(mock_db, test_user):
    mock_db.query().filter().first.return_value = test_user

    result = authenticate_user(mock_db, "testuser", "wrongpassword")

    assert result is False


def test_authenticate_user_not_found(mock_db):
    mock_db.query().filter().first.return_value = None

    result = authenticate_user(mock_db, "unknownuser", "password123")

    assert result is False


@pytest.mark.asyncio
@patch("app.services.user_service.jwt.decode")
async def test_get_current_user_success(mock_jwt_decode, mock_db, test_user):
    mock_jwt_decode.return_value = {"sub": "testuser"}
    mock_db.query().filter().first.return_value = test_user

    result = await get_current_user("fake_token", mock_db)

    assert result.username == "testuser"


@pytest.mark.asyncio
@patch("app.services.user_service.jwt.decode", side_effect=JWTError)
async def test_get_current_user_invalid_token(mock_jwt_decode, mock_db):
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("invalid_token", mock_db)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Невозможно проверить учетные данные" in exc_info.value.detail


def test_register_handler_success(mock_db):
    user_data = UserCreate(
        username="newuser", password="password123",
        email="test@example.com")
    mock_db.query().filter().first.return_value = None

    mock_user = MagicMock()
    mock_user.username = "newuser"

    mock_db.refresh.side_effect = lambda x: x.__dict__.update(
        {"username": "newuser"})

    result = register_handler(user_data, mock_db)

    assert result.username == "newuser"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_register_handler_user_already_exists(mock_db):
    user_data = UserCreate(
        username="existinguser", password="password123",
        email="test@example.com")
    mock_db.query().filter().first.return_value = User(
        id=1, username="existinguser")

    with pytest.raises(HTTPException) as exc_info:
        register_handler(user_data, mock_db)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Такое имя пользователя уже существует" in (
        exc_info.value.detail)


def test_delete_user_handler_success(mock_db, test_user):
    mock_db.query().filter().first.return_value = test_user

    result = delete_user_handler(1, mock_db)

    assert result["detail"] == "Пользователь успешно удалён"
    assert mock_db.query().filter().first.called
    mock_db.delete.assert_called_once_with(test_user)
    mock_db.commit.assert_called_once()


def test_delete_user_handler_not_found(mock_db):
    mock_db.query().filter().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_user_handler(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Пользователь не найден" in exc_info.value.detail
