from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.warehouse import Category
from app.schemas.warehouse import CategoryCreate, CategoryUpdate


def create_category(category_data: CategoryCreate, db: Session):
    """Создание новой категории с проверкой на дубликат"""
    try:
        # Проверяем, существует ли уже такая категория
        existing_category = (
            db.query(Category).filter_by(name=category_data.name).first()
        )
        if existing_category:
            raise HTTPException(
                status_code=400,
                detail="Категория с таким именем уже существует"
            )

        # Создаём новую категорию
        db_category = Category(**category_data.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Ошибка базы данных: {str(e)}")


def get_categories(skip: int, limit: int, db: Session):
    """Получение списка категорий с пагинацией"""
    try:
        return db.query(Category).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка чтения базы данных: {str(e)}"
        )


def get_category(category_id: int, db: Session):
    """Получение категории по ID"""
    category = db.query(Category).filter_by(id=category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return category


def update_category(
        category_id: int, category_data: CategoryUpdate, db: Session):
    """Обновление данных категории"""
    category = db.query(Category).filter_by(id=category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    updated_data = category_data.dict(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(category, key, value)

    try:
        db.commit()
        db.refresh(category)
        return category
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Конфликт данных при обновлении категории: {str(e)}",
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обновления данных в базе: {str(e)}"
        )


def delete_category(category_id: int, db: Session):
    """Удаление категории"""
    category = db.query(Category).filter_by(id=category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    try:
        db.delete(category)
        db.commit()
        return {"detail": "Категория успешно удалена"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении категории: {str(e)}"
        )
