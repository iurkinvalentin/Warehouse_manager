import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException
from app.services.category_service import (
    create_category, get_categories, get_category,
    update_category, delete_category
)
from app.models.warehouse import Category
from app.schemas.warehouse import CategoryCreate, CategoryUpdate


@pytest.fixture
def mock_db():
    """Создает мокнутую сессию SQLAlchemy"""
    return MagicMock()


def test_create_category_success(mock_db):
    """Успешное создание категории"""
    category_data = CategoryCreate(name="Electronics")

    mock_db.query().filter_by().first.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    result = create_category(category_data, mock_db)

    assert result.name == "Electronics"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_create_category_duplicate_error(mock_db):
    """Ошибка: Категория с таким именем уже существует"""
    category_data = CategoryCreate(name="Electronics")

    mock_db.query().filter_by().first.return_value = Category(id=1, name="Electronics")

    with pytest.raises(HTTPException) as exc_info:
        create_category(category_data, mock_db)

    assert exc_info.value.status_code == 400
    assert "Категория с таким именем уже существует" in exc_info.value.detail


def test_create_category_sqlalchemy_error(mock_db):
    """Ошибка базы данных при создании категории"""
    category_data = CategoryCreate(name="Electronics")

    mock_db.query().filter_by().first.return_value = None
    mock_db.commit.side_effect = SQLAlchemyError("DB Error")

    with pytest.raises(HTTPException) as exc_info:
        create_category(category_data, mock_db)

    assert exc_info.value.status_code == 500
    assert "Ошибка базы данных" in exc_info.value.detail


def test_get_categories_success(mock_db):
    """Получение списка категорий"""
    mock_db.query().offset().limit().all.return_value = [
        Category(id=1, name="Electronics"),
        Category(id=2, name="Furniture"),
    ]

    result = get_categories(0, 10, mock_db)

    assert len(result) == 2
    assert result[0].name == "Electronics"
    assert result[1].name == "Furniture"
    mock_db.query().offset().limit().all.assert_called_once()


def test_get_category_found(mock_db):
    """Получение категории по ID (успешно)"""
    category = Category(id=1, name="Electronics")
    mock_db.query().filter_by().first.return_value = category

    result = get_category(1, mock_db)

    assert result.name == "Electronics"
    mock_db.query().filter_by().first.assert_called_once()


def test_get_category_not_found(mock_db):
    """Ошибка: Категория не найдена"""
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_category(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Категория не найдена" in exc_info.value.detail


def test_update_category_success(mock_db):
    """Успешное обновление категории"""
    category = Category(id=1, name="Electronics")
    mock_db.query().filter_by().first.return_value = category

    update_data = CategoryUpdate(name="Updated Electronics")
    result = update_category(1, update_data, mock_db)

    assert result.name == "Updated Electronics"
    mock_db.commit.assert_called_once()


def test_update_category_not_found(mock_db):
    """Ошибка: Обновление несуществующей категории"""
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        update_category(99, CategoryUpdate(name="New Name"), mock_db)

    assert exc_info.value.status_code == 404
    assert "Категория не найдена" in exc_info.value.detail


def test_update_category_integrity_error(mock_db):
    """Ошибка: Конфликт данных при обновлении категории (IntegrityError)"""
    category = Category(id=1, name="Electronics")
    mock_db.query().filter_by().first.return_value = category
    mock_db.commit.side_effect = IntegrityError("IntegrityError", {}, None)

    with pytest.raises(HTTPException) as exc_info:
        update_category(1, CategoryUpdate(name="New Name"), mock_db)

    assert exc_info.value.status_code == 409
    assert "Конфликт данных при обновлении категории" in exc_info.value.detail


def test_delete_category_success(mock_db):
    """Успешное удаление категории"""
    category = Category(id=1, name="Electronics")
    mock_db.query().filter_by().first.return_value = category

    result = delete_category(1, mock_db)

    assert result["detail"] == "Категория успешно удалена"
    mock_db.delete.assert_called_once_with(category)
    mock_db.commit.assert_called_once()


def test_delete_category_not_found(mock_db):
    """Ошибка: Удаление несуществующей категории"""
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_category(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Категория не найдена" in exc_info.value.detail


def test_delete_category_sqlalchemy_error(mock_db):
    """Ошибка базы данных при удалении категории"""
    category = Category(id=1, name="Electronics")
    mock_db.query().filter_by().first.return_value = category
    mock_db.commit.side_effect = SQLAlchemyError("DB Error")

    with pytest.raises(HTTPException) as exc_info:
        delete_category(1, mock_db)

    assert exc_info.value.status_code == 500
    assert "Ошибка при удалении категории" in exc_info.value.detail
