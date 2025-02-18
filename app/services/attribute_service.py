from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.warehouse import Attribute
from app.schemas.warehouse import AttributeCreate, AttributeUpdate


def create_attribute(attribute_data: AttributeCreate, db: Session):
    """Создание нового атрибута товара"""
    try:
        db_attribute = Attribute(**attribute_data.dict())
        db.add(db_attribute)
        db.commit()
        db.refresh(db_attribute)
        return db_attribute
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Ошибка создания аттрибута"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Ошибка базы данных: {str(e)}"
        )


def get_attributes(skip: int, limit: int, db: Session):
    """Получение списка атрибутов с пагинацией"""
    try:
        return db.query(Attribute).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка чтения базы данных: {str(e)}"
        )


def get_attribute(attribute_id: int, db: Session):
    """Получение атрибута по ID"""
    attribute = db.query(Attribute).filter_by(id=attribute_id).first()
    if not attribute:
        raise HTTPException(status_code=404, detail="Атрибут не найден")
    return attribute


def update_attribute(attribute_id: int,
                     attribute_data: AttributeUpdate, db: Session):
    """Обновление данных атрибута"""
    attribute = db.query(Attribute).filter_by(id=attribute_id).first()
    if not attribute:
        raise HTTPException(status_code=404, detail="Атрибут не найден")

    updated_data = attribute_data.dict(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(attribute, key, value)

    try:
        db.commit()
        db.refresh(attribute)
        return attribute
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Конфликт данных при обновлении атрибута: {str(e)}"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обновления данных в базе: {str(e)}"
        )


def delete_attribute(attribute_id: int, db: Session):
    """Удаление атрибута"""
    attribute = db.query(Attribute).filter_by(id=attribute_id).first()
    if not attribute:
        raise HTTPException(status_code=404, detail="Атрибут не найден")

    try:
        db.delete(attribute)
        db.commit()
        return {"detail": "Атрибут успешно удален"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении атрибута: {str(e)}"
        )
