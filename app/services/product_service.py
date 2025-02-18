from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.warehouse import Product, Warehouse, Category
from app.models.user import User
from app.schemas.warehouse import ProductCreate, ProductUpdate, ProductMove


def create_product(
        product_data: ProductCreate, db: Session, current_user: User):
    """Создание нового товара с автоматическим заполнением created_by"""
    try:
        category = db.query(Category).filter_by(id=product_data.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Категория не найдена")
        warehouse = db.query(Warehouse).filter_by(id=product_data.warehouse_id).first()
        if not warehouse:
            raise HTTPException(status_code=400, detail="Склад не найден")
        created_by = current_user.id
        db_product = Product(
            **product_data.dict(exclude={"created_by"}),
            created_by=created_by,
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Товар с таким именем уже существует"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Ошибка базы данных: {str(e)}"
        )


def get_products(skip: int, limit: int, db: Session):
    """Получение списка товаров с пагинацией"""
    try:
        return db.query(Product).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка чтения базы данных: {str(e)}"
        )


def get_product(product_id: int, db: Session):
    """Получение товара по ID"""
    product = db.query(Product).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product


def update_product(
        product_id: int, product_data: ProductUpdate,
        db: Session, current_user: User):
    """Обновление данных товара"""
    product = db.query(Product).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    updated_data = product_data.dict(exclude_unset=True)
    if "category_id" in updated_data:
        category = db.query(Category).filter_by(id=updated_data["category_id"]).first()
        if not category:
            raise HTTPException(status_code=400, detail="Категория не найдена")
    if "warehouse_id" in updated_data:
        warehouse = db.query(Warehouse).filter_by(
            id=updated_data["warehouse_id"]).first()
        if not warehouse:
            raise HTTPException(status_code=400, detail="Склад не найден")
    for key, value in updated_data.items():
        setattr(product, key, value)
    product.updated_by = current_user.id
    db.commit()
    db.refresh(product)
    return product
 

def delete_product(product_id: int, db: Session):
    """Удаление товара"""
    product = db.query(Product).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    db.delete(product)
    db.commit()
    return {"detail": "Товар успешно удален"}


def move_product(product_id: int, move_data: ProductMove, db: Session, current_user: User):
    """Перемещение товара между складами с обновлением updated_by."""
    
    product = db.query(Product).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    source_warehouse = db.query(Warehouse).filter_by(id=move_data.source_warehouse_id).first()
    if not source_warehouse:
        raise HTTPException(status_code=404, detail="Исходный склад не найден")

    destination_warehouse = db.query(Warehouse).filter_by(id=move_data.destination_warehouse_id).first()
    if not destination_warehouse:
        raise HTTPException(status_code=404, detail="Целевой склад не найден")

    if product.warehouse_id != move_data.source_warehouse_id:
        raise HTTPException(status_code=400, detail="Товар не находится на указанном складе")

    # Обновляем склад у товара
    product.warehouse_id = move_data.destination_warehouse_id

    # Фиксируем, кто переместил товар
    product.updated_by = current_user.id


    db.commit()
    db.refresh(product)
    return {"detail": f"Товар {product.name} перемещен на склад {destination_warehouse.name}"}


