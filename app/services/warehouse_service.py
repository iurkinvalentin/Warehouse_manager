from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate


def create_warehouse(warehouse_data: WarehouseCreate, db: Session):
    """Создание нового склада"""
    try:
        db_warehouse = Warehouse(**warehouse_data.dict())
        db.add(db_warehouse)
        db.commit()
        db.refresh(db_warehouse)
        return db_warehouse
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail=(
                "Склад с таким именем или адресом уже существует"
                )
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Ошибка базы данных: {str(e)}"
            )


def get_warehouses(skip: int, limit: int, db: Session):
    """Получение списка складов с пагинацией"""
    try:
        return db.query(Warehouse).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка чтения базы данных: {str(e)}"
        )


def get_warehouse(warehouse_id: int, db: Session):
    """Получение одного склада по ID"""
    warehouse = db.query(Warehouse).filter_by(id=warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Склад не найден")
    return warehouse


def update_warehouse(
        warehouse_id: int, warehouse_data: WarehouseUpdate, db: Session):
    """Обновление данных склада"""
    warehouse = db.query(Warehouse).filter_by(id=warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Склад не найден")

    updated_data = warehouse_data.dict(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(warehouse, key, value)

    try:
        db.commit()
        db.refresh(warehouse)
        return warehouse
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Конфликт данных при обновлении склада: {str(e)}"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обновления данных в базе: {str(e)}"
        )


def delete_warehouse(warehouse_id: int, db: Session):
    """Удаление склада"""
    warehouse = db.query(Warehouse).filter_by(id=warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Склад не найден")

    try:
        db.delete(warehouse)
        db.commit()
        return {"detail": "Склад успешно удален"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении склада: {str(e)}"
        )
