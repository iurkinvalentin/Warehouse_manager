from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate
from app.services.warehouse_service import (
    create_warehouse,
    delete_warehouse,
    get_warehouse,
    get_warehouses,
    update_warehouse,
)


@pytest.fixture
def mock_db():
    return MagicMock()


def test_create_warehouse_success(mock_db):
    warehouse_data = WarehouseCreate(
        name="Test Warehouse", address="123 Main St")

    mock_warehouse = MagicMock()
    mock_warehouse.name = "Test Warehouse"
    mock_warehouse.address = "123 Main St"

    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda x: x.__dict__.update(
        mock_warehouse.__dict__)

    result = create_warehouse(warehouse_data, mock_db)

    assert result.name == "Test Warehouse"
    assert result.address == "123 Main St"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_create_warehouse_missing_field():
    with pytest.raises(ValidationError) as exc_info:
        WarehouseCreate()

    assert "name" in str(exc_info.value)
    assert "address" in str(exc_info.value)


def test_create_warehouse_integrity_error(mock_db):
    warehouse_data = WarehouseCreate(
        name="Duplicate Warehouse", address="City B")
    mock_db.commit.side_effect = IntegrityError("IntegrityError", {}, None)

    with pytest.raises(HTTPException) as exc_info:
        create_warehouse(warehouse_data, mock_db)

    assert exc_info.value.status_code == 400
    assert "Склад с таким именем уже существует" in exc_info.value.detail
    mock_db.rollback.assert_called_once()


def test_get_warehouses_success(mock_db):
    warehouses = [
        Warehouse(id=1, name="WH1", address="Addr1"),
        Warehouse(id=2, name="WH2", address="Addr2"),
    ]
    mock_query = MagicMock()
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = warehouses

    mock_db.query.return_value = mock_query

    result = get_warehouses(0, 10, mock_db)

    assert len(result) == 2
    assert result[0].name == "WH1"
    assert result[1].name == "WH2"
    mock_query.all.assert_called_once()


def test_get_warehouse_found(mock_db):
    warehouse = Warehouse(id=1, name="WH1", address="Addr1")
    mock_db.query().filter_by().first.return_value = warehouse

    result = get_warehouse(1, mock_db)

    assert result.name == "WH1"
    assert result.address == "Addr1"
    mock_db.query().filter_by().first.assert_called_once()


def test_get_warehouse_not_found(mock_db):
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_warehouse(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Склад не найден" in exc_info.value.detail


def test_update_warehouse_success(mock_db):
    warehouse = Warehouse(id=1, name="WH1", address="Addr1")
    mock_db.query().filter_by().first.return_value = warehouse

    update_data = WarehouseUpdate(name="Updated WH")
    result = update_warehouse(1, update_data, mock_db)

    assert result.name == "Updated WH"
    assert warehouse.name == "Updated WH"
    mock_db.commit.assert_called_once()


def test_update_warehouse_not_found(mock_db):
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        update_warehouse(99, WarehouseUpdate(name="New Name"), mock_db)

    assert exc_info.value.status_code == 404
    assert "Склад не найден" in exc_info.value.detail


def test_delete_warehouse_success(mock_db):
    warehouse = Warehouse(id=1, name="WH1", address="Addr1")
    mock_db.query().filter_by().first.return_value = warehouse

    result = delete_warehouse(1, mock_db)

    assert result["detail"] == "Склад успешно удален"
    mock_db.delete.assert_called_once_with(warehouse)
    mock_db.commit.assert_called_once()


def test_delete_warehouse_not_found(mock_db):
    mock_db.query().filter_by().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_warehouse(99, mock_db)

    assert exc_info.value.status_code == 404
    assert "Склад не найден" in exc_info.value.detail
