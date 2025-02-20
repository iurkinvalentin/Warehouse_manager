from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.warehouse import Category
from app.schemas.warehouse import CategoryCreate, CategoryUpdate
from app.services.category_service import (
    create_category,
    delete_category,
    get_categories,
    get_category,
    update_category,
)


@pytest.fixture
def mock_db():
    return MagicMock()


def test_create_category_success(mock_db):
    category_data = CategoryCreate(name="Electronics")

    mock_db.query().filter_by().first.return_value = None
    mock_db.refresh.side_effect = lambda x: x.__dict__.update(
        {"name": "Electronics"})

    result = create_category(category_data, mock_db)

    assert result.name == "Electronics"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_create_category_duplicate_error(mock_db):
    category_data = CategoryCreate(name="Electronics")

    mock_db.query().filter_by().first.return_value = Category(
        id=1, name="Electronics")

    with pytest.raises(HTTPException) as exc_info:
        create_category(category_data, mock_db)

    assert exc_info.value.status_code == 400
    assert "Категория с таким именем уже существует" in exc_info.value.detail


def test_create_category_sqlalchemy_error(mock_db):
    category_data = CategoryCreate(name="Electronics")

    mock_db.query().filter_by().first.return_value = None
    mock_db.commit.side_effect = SQLAlchemyError("DB Error")

    with pytest.raises(HTTPException) as exc_info:
        create_category(category_data, mock_db)

    assert exc_info.value.status_code == 500
    assert "Ошибка базы данных" in exc_info.value.detail


def test_get_categories_success(mock_db):
    categories = [
        Category(id=1, name="Electronics"),
        Category(id=2, name="Furniture"),
    ]
    mock_query = MagicMock()
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = categories

    mock_db.query.return_value = mock_query

    result = get_categories(0, 10, mock_db)

    assert len(result) == 2
    assert result[0].name == "Electronics"
    assert result[1].name == "Furniture"
    mock_query.all.assert_called_once()


def test_get_category_found(mock_db):
    category = Category(id=1, name="Electronics")
    mock_db.query().filter_by().first.return_value = category

    result = get_category(1, mock_db)

    assert result.name == "Electronics"
    mock_db.query().filter_by().first.assert_called_once()


def test_get_category_not_found(mock_db):
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_category(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Категория не найдена" in exc_info.value.detail


def test_update_category_success(mock_db):
    category = Category(id=1, name="Electronics")
    mock_db.query().filter_by().first.return_value = category

    update_data = CategoryUpdate(name="Updated Electronics")
    result = update_category(1, update_data, mock_db)

    assert result.name == "Updated Electronics"
    assert category.name == "Updated Electronics"
    mock_db.commit.assert_called_once()


def test_update_category_not_found(mock_db):
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        update_category(99, CategoryUpdate(name="New Name"), mock_db)

    assert exc_info.value.status_code == 404
    assert "Категория не найдена" in exc_info.value.detail


def test_update_category_integrity_error(mock_db):
    category = Category(id=1, name="Electronics")
    mock_db.query().filter_by().first.return_value = category
    mock_db.commit.side_effect = IntegrityError("IntegrityError", {}, None)

    with pytest.raises(HTTPException) as exc_info:
        update_category(1, CategoryUpdate(name="New Name"), mock_db)

    assert exc_info.value.status_code == 409
    assert "Конфликт данных" in exc_info.value.detail


def test_delete_category_success(mock_db):
    category = Category(id=1, name="Electronics")
    mock_db.query().filter_by().first.return_value = category

    result = delete_category(1, mock_db)

    assert result["detail"] == "Категория успешно удалена"
    assert mock_db.query().filter_by().first.called
    mock_db.delete.assert_called_once_with(category)
    mock_db.commit.assert_called_once()


def test_delete_category_not_found(mock_db):
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_category(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Категория не найдена" in exc_info.value.detail


def test_delete_category_sqlalchemy_error(mock_db):
    category = Category(id=1, name="Electronics")
    mock_db.query().filter_by().first.return_value = category
    mock_db.commit.side_effect = SQLAlchemyError("DB Error")

    with pytest.raises(HTTPException) as exc_info:
        delete_category(1, mock_db)

    assert exc_info.value.status_code == 500
    assert "Ошибка при удалении категории" in exc_info.value.detail
