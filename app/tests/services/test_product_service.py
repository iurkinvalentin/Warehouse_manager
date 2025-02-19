import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.services.product_service import (
    create_product, get_products, get_product,
    update_product, delete_product, move_product
)
from app.models.warehouse import Product, Warehouse, Category
from app.models.user import User
from app.schemas.warehouse import ProductCreate, ProductUpdate, ProductMove
from app.schemas.utils import QueryParams


@pytest.fixture
def mock_db():
    """Создает мокнутую сессию SQLAlchemy"""
    return MagicMock()


@pytest.fixture
def mock_user():
    """Создает тестового пользователя"""
    return User(id=1, username="test_user")


def test_create_product_success(mock_db, mock_user):
    """Успешное создание товара"""
    product_data = ProductCreate(name="Test Product", category_id=1, warehouse_id=1, quantity=10)

    mock_db.query().filter_by().first.side_effect = [Category(id=1, name="Electronics"), Warehouse(id=1, name="WH1")]
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    result = create_product(product_data, mock_db, mock_user)

    assert result.name == "Test Product"
    assert result.quantity == 10
    assert result.created_by == mock_user.id
    mock_db.add.assert_called_once()


def test_create_product_category_not_found(mock_db, mock_user):
    """Ошибка: Категория не найдена"""
    product_data = ProductCreate(name="Test Product", category_id=1, warehouse_id=1, quantity=10)

    mock_db.query().filter_by().first.side_effect = [None, Warehouse(id=1, name="WH1")]

    with pytest.raises(HTTPException) as exc_info:
        create_product(product_data, mock_db, mock_user)

    assert exc_info.value.status_code == 400
    assert "Категория не найдена" in exc_info.value.detail


def test_create_product_warehouse_not_found(mock_db, mock_user):
    """Ошибка: Склад не найден"""
    product_data = ProductCreate(name="Test Product", category_id=1, warehouse_id=1, quantity=10)

    mock_db.query().filter_by().first.side_effect = [Category(id=1, name="Electronics"), None]

    with pytest.raises(HTTPException) as exc_info:
        create_product(product_data, mock_db, mock_user)

    assert exc_info.value.status_code == 400
    assert "Склад не найден" in exc_info.value.detail


def test_create_product_integrity_error(mock_db, mock_user):
    """Ошибка: Продукт с таким именем уже существует (IntegrityError)"""
    product_data = ProductCreate(name="Test Product", category_id=1, warehouse_id=1, quantity=10)

    mock_db.query().filter_by().first.side_effect = [Category(id=1, name="Electronics"), Warehouse(id=1, name="WH1")]
    mock_db.commit.side_effect = IntegrityError("IntegrityError", {}, None)

    with pytest.raises(HTTPException) as exc_info:
        create_product(product_data, mock_db, mock_user)

    assert exc_info.value.status_code == 400
    assert "Товар с таким именем уже существует" in exc_info.value.detail


def test_get_products(mock_db):
    """Получение списка товаров"""
    mock_db.query().all.return_value = [
        Product(id=1, name="Product1", quantity=5),
        Product(id=2, name="Product2", quantity=8),
    ]

    query_params = QueryParams()
    result = get_products(mock_db, query_params)

    assert len(result) == 2
    assert result[0].name == "Product1"
    assert result[1].name == "Product2"
    mock_db.query().all.assert_called_once()


def test_get_product_found(mock_db):
    """Получение товара по ID (успешно)"""
    product = Product(id=1, name="Test Product", quantity=10)
    mock_db.query().filter_by().first.return_value = product

    result = get_product(1, mock_db)

    assert result.name == "Test Product"
    assert result.quantity == 10
    mock_db.query().filter_by().first.assert_called_once()


def test_get_product_not_found(mock_db):
    """Ошибка: Товар не найден"""
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_product(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Товар не найден" in exc_info.value.detail


def test_update_product_success(mock_db, mock_user):
    """Успешное обновление товара"""
    product = Product(id=1, name="Test Product", quantity=10)
    mock_db.query().filter_by().first.return_value = product

    update_data = ProductUpdate(name="Updated Product", quantity=20)
    result = update_product(1, update_data, mock_db, mock_user)

    assert result.name == "Updated Product"
    assert result.quantity == 20
    assert result.updated_by == mock_user.id
    mock_db.commit.assert_called_once()


def test_update_product_not_found(mock_db, mock_user):
    """Ошибка: Обновление несуществующего товара"""
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        update_product(99, ProductUpdate(name="New Name"), mock_db, mock_user)

    assert exc_info.value.status_code == 404
    assert "Товар не найден" in exc_info.value.detail


def test_delete_product_success(mock_db):
    """Успешное удаление товара"""
    product = Product(id=1, name="Test Product", quantity=10)
    mock_db.query().filter_by().first.return_value = product

    result = delete_product(1, mock_db)

    assert result["detail"] == "Товар успешно удален"
    mock_db.delete.assert_called_once_with(product)
    mock_db.commit.assert_called_once()


def test_delete_product_not_found(mock_db):
    """Ошибка: Удаление несуществующего товара"""
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_product(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Товар не найден" in exc_info.value.detail


def test_move_product_success(mock_db, mock_user):
    """Успешное перемещение товара на другой склад"""
    product = Product(id=1, name="Test Product", quantity=10, warehouse_id=1)
    new_warehouse = Warehouse(id=2, name="WH2")

    mock_db.query().filter_by().first.side_effect = [product, new_warehouse]

    move_data = ProductMove(destination_warehouse_id=2)
    result = move_product(1, move_data, mock_db, mock_user)

    assert result.warehouse_id == 2
    assert result.updated_by == mock_user.id
    mock_db.commit.assert_called_once()


def test_move_product_warehouse_not_found(mock_db, mock_user):
    """Ошибка: Целевой склад не найден"""
    product = Product(id=1, name="Test Product", quantity=10, warehouse_id=1)
    mock_db.query().filter_by().first.side_effect = [product, None]

    move_data = ProductMove(destination_warehouse_id=99)

    with pytest.raises(HTTPException) as exc_info:
        move_product(1, move_data, mock_db, mock_user)

    assert exc_info.value.status_code == 404
    assert "Целевой склад не найден" in exc_info.value.detail
