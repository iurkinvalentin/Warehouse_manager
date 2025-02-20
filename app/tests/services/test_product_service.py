from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.warehouse import Category, Product, Warehouse
from app.schemas.utils import QueryParams
from app.schemas.warehouse import ProductCreate, ProductMove, ProductUpdate
from app.services.product_service import (
    create_product,
    delete_product,
    get_product,
    get_products,
    move_product,
    update_product,
)


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_user():
    return User(id=1, username="test_user")


def test_create_product_success(mock_db, mock_user):
    product_data = ProductCreate(
        name="Test Product", category_id=1, warehouse_id=1, quantity=10)

    mock_db.query().filter_by().first.side_effect = [
        Category(id=1, name="Electronics"),
        Warehouse(id=1, name="WH1"),
    ]
    mock_db.refresh.side_effect = lambda x: x.__dict__.update(
        {"name": "Test Product", "quantity": 10, "created_by": mock_user.id})

    result = create_product(product_data, mock_db, mock_user)

    assert result.name == "Test Product"
    assert result.quantity == 10
    assert result.created_by == mock_user.id
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_create_product_category_not_found(mock_db, mock_user):
    product_data = ProductCreate(
        name="Test Product", category_id=1, warehouse_id=1, quantity=10)

    mock_db.query().filter_by().first.side_effect = [None, Warehouse(
        id=1, name="WH1")]

    with pytest.raises(HTTPException) as exc_info:
        create_product(product_data, mock_db, mock_user)

    assert exc_info.value.status_code == 400
    assert "Категория не найдена" in exc_info.value.detail


def test_create_product_warehouse_not_found(mock_db, mock_user):
    product_data = ProductCreate(
        name="Test Product", category_id=1, warehouse_id=1, quantity=10)

    mock_db.query().filter_by().first.side_effect = [Category(
        id=1, name="Electronics"), None]

    with pytest.raises(HTTPException) as exc_info:
        create_product(product_data, mock_db, mock_user)

    assert exc_info.value.status_code == 400
    assert "Склад не найден" in exc_info.value.detail


def test_create_product_integrity_error(mock_db, mock_user):
    product_data = ProductCreate(
        name="Test Product", category_id=1, warehouse_id=1, quantity=10)

    mock_db.query().filter_by().first.side_effect = [Category(
        id=1, name="Electronics"), Warehouse(id=1, name="WH1")]
    mock_db.commit.side_effect = IntegrityError("IntegrityError", {}, None)

    with pytest.raises(HTTPException) as exc_info:
        create_product(product_data, mock_db, mock_user)

    assert exc_info.value.status_code == 400
    assert "Товар с таким именем уже существует" in exc_info.value.detail


def test_get_products(mock_db):
    products = [
        Product(id=1, name="Product1", quantity=5),
        Product(id=2, name="Product2", quantity=8),
    ]
    mock_query = MagicMock()
    mock_query.all.return_value = products
    mock_db.query.return_value = mock_query

    query_params = QueryParams()
    result = get_products(mock_db, query_params)

    assert len(result) == 2
    assert result[0].name == "Product1"
    assert result[1].name == "Product2"
    mock_query.all.assert_called_once()


def test_get_product_found(mock_db):
    product = Product(id=1, name="Test Product", quantity=10)
    mock_db.query().filter_by().first.return_value = product

    result = get_product(1, mock_db)

    assert result.name == "Test Product"
    assert result.quantity == 10
    mock_db.query().filter_by().first.assert_called_once()


def test_get_product_not_found(mock_db):
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_product(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Товар не найден" in exc_info.value.detail


def test_update_product_success(mock_db, mock_user):
    product = Product(id=1, name="Test Product", quantity=10)
    mock_db.query().filter_by().first.return_value = product

    update_data = ProductUpdate(name="Updated Product", quantity=20)
    result = update_product(1, update_data, mock_db, mock_user)

    assert result.name == "Updated Product"
    assert result.quantity == 20
    assert product.name == "Updated Product"
    assert product.updated_by == mock_user.id
    mock_db.commit.assert_called_once()


def test_update_product_not_found(mock_db, mock_user):
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        update_product(99, ProductUpdate(name="New Name"), mock_db, mock_user)

    assert exc_info.value.status_code == 404
    assert "Товар не найден" in exc_info.value.detail


def test_delete_product_success(mock_db):
    product = Product(id=1, name="Test Product", quantity=10)
    mock_db.query().filter_by().first.return_value = product

    result = delete_product(1, mock_db)

    assert result["detail"] == "Товар успешно удален"
    mock_db.delete.assert_called_once_with(product)
    mock_db.commit.assert_called_once()


def test_delete_product_not_found(mock_db):
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_product(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Товар не найден" in exc_info.value.detail


def test_move_product_success(mock_db, mock_user):
    product = Product(id=1, name="Test Product", quantity=10, warehouse_id=1)
    new_warehouse = Warehouse(id=2, name="WH2")

    mock_db.query().filter_by().first.side_effect = [product, new_warehouse]

    move_data = ProductMove(destination_warehouse_id=2)
    result = move_product(1, move_data, mock_db, mock_user)

    assert result.warehouse_id == 2
    assert product.warehouse_id == 2
    assert product.updated_by == mock_user.id
    mock_db.commit.assert_called_once()


def test_move_product_warehouse_not_found(mock_db, mock_user):
    product = Product(id=1, name="Test Product", quantity=10, warehouse_id=1)
    mock_db.query().filter_by().first.side_effect = [product, None]

    move_data = ProductMove(destination_warehouse_id=99)

    with pytest.raises(HTTPException) as exc_info:
        move_product(1, move_data, mock_db, mock_user)

    assert exc_info.value.status_code == 404
    assert "Целевой склад не найден" in exc_info.value.detail
