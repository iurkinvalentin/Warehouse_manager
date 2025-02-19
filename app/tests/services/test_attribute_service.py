import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException
from app.services.attribute_service import (
    create_attribute, get_attributes, get_attribute,
    update_attribute, delete_attribute
)
from app.models.warehouse import Attribute, Product
from app.schemas.warehouse import AttributeCreate, AttributeUpdate


@pytest.fixture
def mock_db():
    """Создает мокнутую сессию SQLAlchemy"""
    return MagicMock()


def test_create_attribute_success(mock_db):
    """Успешное создание атрибута"""
    attribute_data = AttributeCreate(name="Color", value="Red", product_id=1)

    # Симулируем, что товар существует, а атрибут нет
    mock_db.query().filter_by().first.side_effect = [
        Product(id=1, name="Test Product"),  # Товар найден
        None  # Атрибут не найден → можно создать
    ]
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    result = create_attribute(attribute_data, mock_db)

    assert result.name == "Color"
    assert result.value == "Red"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_create_attribute_product_not_found(mock_db):
    """Ошибка: Товар не найден"""
    attribute_data = AttributeCreate(name="Color", value="Red", product_id=1)

    mock_db.query().filter_by().first.side_effect = [None]  # Товар не найден

    with pytest.raises(HTTPException) as exc_info:
        create_attribute(attribute_data, mock_db)

    assert exc_info.value.status_code == 400
    assert "Товар не найден" in exc_info.value.detail


def test_create_attribute_already_exists(mock_db):
    """Ошибка: Атрибут уже существует"""
    attribute_data = AttributeCreate(name="Color", value="Red", product_id=1)

    mock_db.query().filter_by().first.side_effect = [
        Product(id=1, name="Test Product"),  # Товар найден
        Attribute(id=1, name="Color", value="Red")  # Атрибут уже существует
    ]

    with pytest.raises(HTTPException) as exc_info:
        create_attribute(attribute_data, mock_db)

    assert exc_info.value.status_code == 400
    assert "Характериситика уже существует в бд" in exc_info.value.detail


def test_create_attribute_sqlalchemy_error(mock_db):
    """Ошибка базы данных при создании атрибута"""
    attribute_data = AttributeCreate(name="Color", value="Red", product_id=1)

    mock_db.query().filter_by().first.side_effect = [
        Product(id=1, name="Test Product"), None  # Товар найден, атрибута нет
    ]
    mock_db.commit.side_effect = SQLAlchemyError("DB Error")

    with pytest.raises(HTTPException) as exc_info:
        create_attribute(attribute_data, mock_db)

    assert exc_info.value.status_code == 500
    assert "Ошибка базы данных" in exc_info.value.detail


def test_get_attributes_success(mock_db):
    """Получение списка атрибутов"""
    mock_db.query().offset().limit().all.return_value = [
        Attribute(id=1, name="Color", value="Red"),
        Attribute(id=2, name="Size", value="Large"),
    ]

    result = get_attributes(0, 10, mock_db)

    assert len(result) == 2
    assert result[0].name == "Color"
    assert result[1].name == "Size"
    mock_db.query().offset().limit().all.assert_called_once()


def test_get_attribute_found(mock_db):
    """Получение атрибута по ID (успешно)"""
    attribute = Attribute(id=1, name="Color", value="Red")
    mock_db.query().filter_by().first.return_value = attribute

    result = get_attribute(1, mock_db)

    assert result.name == "Color"
    assert result.value == "Red"
    mock_db.query().filter_by().first.assert_called_once()


def test_get_attribute_not_found(mock_db):
    """Ошибка: Атрибут не найден"""
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_attribute(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Атрибут не найден" in exc_info.value.detail


def test_update_attribute_success(mock_db):
    """Успешное обновление атрибута"""
    attribute = Attribute(id=1, name="Color", value="Red")
    mock_db.query().filter_by().first.return_value = attribute

    update_data = AttributeUpdate(value="Blue")
    result = update_attribute(1, update_data, mock_db)

    assert result.value == "Blue"
    mock_db.commit.assert_called_once()


def test_update_attribute_not_found(mock_db):
    """Ошибка: Обновление несуществующего атрибута"""
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        update_attribute(99, AttributeUpdate(value="Blue"), mock_db)

    assert exc_info.value.status_code == 404
    assert "Атрибут не найден" in exc_info.value.detail


def test_update_attribute_integrity_error(mock_db):
    """Ошибка: Конфликт данных при обновлении атрибута (IntegrityError)"""
    attribute = Attribute(id=1, name="Color", value="Red")
    mock_db.query().filter_by().first.return_value = attribute
    mock_db.commit.side_effect = IntegrityError("IntegrityError", {}, None)

    with pytest.raises(HTTPException) as exc_info:
        update_attribute(1, AttributeUpdate(value="Blue"), mock_db)

    assert exc_info.value.status_code == 409
    assert "Конфликт данных при обновлении атрибута" in exc_info.value.detail


def test_delete_attribute_success(mock_db):
    """Успешное удаление атрибута"""
    attribute = Attribute(id=1, name="Color", value="Red")
    mock_db.query().filter_by().first.return_value = attribute

    result = delete_attribute(1, mock_db)

    assert result["detail"] == "Атрибут успешно удален"
    mock_db.delete.assert_called_once_with(attribute)
    mock_db.commit.assert_called_once()


def test_delete_attribute_not_found(mock_db):
    """Ошибка: Удаление несуществующего атрибута"""
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_attribute(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Атрибут не найден" in exc_info.value.detail


def test_delete_attribute_sqlalchemy_error(mock_db):
    """Ошибка базы данных при удалении атрибута"""
    attribute = Attribute(id=1, name="Color", value="Red")
    mock_db.query().filter_by().first.return_value = attribute
    mock_db.commit.side_effect = SQLAlchemyError("DB Error")

    with pytest.raises(HTTPException) as exc_info:
        delete_attribute(1, mock_db)

    assert exc_info.value.status_code == 500
    assert "Ошибка при удалении атрибута" in exc_info.value.detail
