import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.services.warehouse_service import (
    create_warehouse, get_warehouses, get_warehouse,
    update_warehouse, delete_warehouse
)
from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate
from pydantic import ValidationError


@pytest.fixture
def mock_db():
    """Создает мок-объект базы данных"""
    return MagicMock()


def test_create_warehouse_success(mock_db):
    """Успешное создание склада"""
    warehouse_data = WarehouseCreate(
        name="Test Warehouse",
        address="123 Main St"
    )

    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    result = create_warehouse(warehouse_data, mock_db)

    assert result.name == "Test Warehouse"
    assert result.address == "123 Main St"
    mock_db.add.assert_called_once()


def test_create_warehouse_missing_field(mock_db):
    """Ошибка при отсутствии обязательного поля (ValidationError)"""
    with pytest.raises(ValidationError) as exc_info:
        warehouse_data = WarehouseCreate(
            name="Test Warehouse"  # Пропущено поле address
        )

    assert "address" in str(exc_info.value)


def test_create_warehouse_integrity_error(mock_db):
    """Ошибка при дублировании склада (IntegrityError)"""
    warehouse_data = WarehouseCreate(
        name="Duplicate Warehouse",
        address="City B"
    )

    mock_db.commit.side_effect = IntegrityError("IntegrityError", {}, None)

    with pytest.raises(Exception) as exc_info:
        create_warehouse(warehouse_data, mock_db)

    assert exc_info.value.status_code == 400
    assert "Склад с таким именем уже существует" in exc_info.value.detail


def test_get_warehouses_success(mock_db):
    """Получение списка складов"""
    mock_db.query().offset().limit().all.return_value = [
        Warehouse(id=1, name="WH1", address="Addr1"),
        Warehouse(id=2, name="WH2", address="Addr2"),
    ]

    result = get_warehouses(0, 10, mock_db)

    assert len(result) == 2
    assert result[0].name == "WH1"
    assert result[1].name == "WH2"
    mock_db.query().offset().limit().all.assert_called_once()


def test_get_warehouse_found(mock_db):
    """Получение склада по ID (найден)"""
    warehouse = Warehouse(id=1, name="WH1", address="Addr1")
    mock_db.query().filter_by().first.return_value = warehouse

    result = get_warehouse(1, mock_db)

    assert result.name == "WH1"
    assert result.address == "Addr1"
    mock_db.query().filter_by().first.assert_called_once()


def test_get_warehouse_not_found(mock_db):
    """Попытка получить несуществующий склад"""
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(Exception) as exc_info:
        get_warehouse(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Склад не найден" in exc_info.value.detail


def test_update_warehouse_success(mock_db):
    """Обновление склада (успешно)"""
    warehouse = Warehouse(id=1, name="WH1", address="Addr1")
    mock_db.query().filter_by().first.return_value = warehouse

    update_data = WarehouseUpdate(name="Updated WH")
    result = update_warehouse(1, update_data, mock_db)

    assert result.name == "Updated WH"
    mock_db.commit.assert_called_once()


def test_update_warehouse_not_found(mock_db):
    """Обновление несуществующего склада"""
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(Exception) as exc_info:
        update_warehouse(99, WarehouseUpdate(name="New Name"), mock_db)

    assert exc_info.value.status_code == 404
    assert "Склад не найден" in exc_info.value.detail


def test_delete_warehouse_success(mock_db):
    """Удаление склада (успешно)"""
    warehouse = Warehouse(id=1, name="WH1", address="Addr1")
    mock_db.query().filter_by().first.return_value = warehouse

    result = delete_warehouse(1, mock_db)

    assert result["detail"] == "Склад успешно удален"
    mock_db.delete.assert_called_once_with(warehouse)
    mock_db.commit.assert_called_once()


def test_delete_warehouse_not_found(mock_db):
    """Удаление несуществующего склада"""
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(Exception) as exc_info:
        delete_warehouse(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Склад не найден" in exc_info.value.detail
