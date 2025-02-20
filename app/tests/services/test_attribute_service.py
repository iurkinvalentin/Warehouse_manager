from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.warehouse import Attribute, Product
from app.schemas.warehouse import AttributeCreate, AttributeUpdate
from app.services.attribute_service import (
    create_attribute,
    delete_attribute,
    get_attribute,
    get_attributes,
    update_attribute,
)


@pytest.fixture
def mock_db():
    return MagicMock()


def test_create_attribute_success(mock_db):
    attribute_data = AttributeCreate(name="Color", value="Red", product_id=1)

    mock_product = Product(id=1, name="Test Product")
    mock_attribute = Attribute(id=1, name="Color", value="Red", product_id=1)

    mock_db.query().filter_by().first.side_effect = [mock_product, None]
    mock_db.refresh.side_effect = lambda x: x.__dict__.update(
        mock_attribute.__dict__)

    result = create_attribute(attribute_data, mock_db)

    assert result.name == "Color"
    assert result.value == "Red"
    assert result.product_id == 1
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_create_attribute_product_not_found(mock_db):
    attribute_data = AttributeCreate(name="Color", value="Red", product_id=1)

    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        create_attribute(attribute_data, mock_db)

    assert exc_info.value.status_code == 400
    assert "Товар не найден" in exc_info.value.detail


def test_create_attribute_already_exists(mock_db):
    attribute_data = AttributeCreate(name="Color", value="Red", product_id=1)

    mock_db.query().filter_by().first.side_effect = [
        Product(id=1, name="Test Product"),
        Attribute(id=1, name="Color", value="Red"),
    ]

    with pytest.raises(HTTPException) as exc_info:
        create_attribute(attribute_data, mock_db)

    assert exc_info.value.status_code == 400
    assert "Характеристика уже существует" in exc_info.value.detail


def test_create_attribute_sqlalchemy_error(mock_db):
    attribute_data = AttributeCreate(name="Color", value="Red", product_id=1)

    mock_db.query().filter_by().first.side_effect = [
        Product(id=1, name="Test Product"),
        None,
    ]
    mock_db.commit.side_effect = SQLAlchemyError("DB Error")

    with pytest.raises(HTTPException) as exc_info:
        create_attribute(attribute_data, mock_db)

    assert exc_info.value.status_code == 500
    assert "Ошибка базы данных" in exc_info.value.detail


def test_get_attributes_success(mock_db):
    attributes = [
        Attribute(id=1, name="Color", value="Red"),
        Attribute(id=2, name="Size", value="Large"),
    ]
    mock_query = MagicMock()
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = attributes

    mock_db.query.return_value = mock_query

    result = get_attributes(0, 10, mock_db)

    assert len(result) == 2
    assert result[0].name == "Color"
    assert result[1].name == "Size"
    mock_query.all.assert_called_once()


def test_get_attribute_found(mock_db):
    attribute = Attribute(id=1, name="Color", value="Red")
    mock_db.query().filter_by().first.return_value = attribute

    result = get_attribute(1, mock_db)

    assert result.name == "Color"
    assert result.value == "Red"
    mock_db.query().filter_by().first.assert_called_once()


def test_get_attribute_not_found(mock_db):
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_attribute(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Атрибут не найден" in exc_info.value.detail


def test_update_attribute_success(mock_db):
    attribute = Attribute(id=1, name="Color", value="Red")
    mock_db.query().filter_by().first.return_value = attribute

    update_data = AttributeUpdate(value="Blue")
    result = update_attribute(1, update_data, mock_db)

    assert result.value == "Blue"
    assert attribute.value == "Blue"
    mock_db.commit.assert_called_once()


def test_update_attribute_not_found(mock_db):
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        update_attribute(99, AttributeUpdate(value="Blue"), mock_db)

    assert exc_info.value.status_code == 404
    assert "Атрибут не найден" in exc_info.value.detail


def test_update_attribute_integrity_error(mock_db):
    attribute = Attribute(id=1, name="Color", value="Red")
    mock_db.query().filter_by().first.return_value = attribute
    mock_db.commit.side_effect = IntegrityError("IntegrityError", {}, None)

    with pytest.raises(HTTPException) as exc_info:
        update_attribute(1, AttributeUpdate(value="Blue"), mock_db)

    assert exc_info.value.status_code == 409
    assert "Конфликт данных" in exc_info.value.detail


def test_delete_attribute_success(mock_db):
    attribute = Attribute(id=1, name="Color", value="Red")
    mock_db.query().filter_by().first.return_value = attribute

    result = delete_attribute(1, mock_db)

    assert result["detail"] == "Атрибут успешно удален"
    assert mock_db.query().filter_by().first.called
    mock_db.delete.assert_called_once_with(attribute)
    mock_db.commit.assert_called_once()


def test_delete_attribute_not_found(mock_db):
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_attribute(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Атрибут не найден" in exc_info.value.detail


def test_delete_attribute_sqlalchemy_error(mock_db):
    attribute = Attribute(id=1, name="Color", value="Red")
    mock_db.query().filter_by().first.return_value = attribute
    mock_db.commit.side_effect = SQLAlchemyError("DB Error")

    with pytest.raises(HTTPException) as exc_info:
        delete_attribute(1, mock_db)

    assert exc_info.value.status_code == 500
    assert "Ошибка при удалении атрибута" in exc_info.value.detail
