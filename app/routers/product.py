from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.data.database import get_db
from app.services import product_service
from app.models.user import User
from app.schemas.warehouse import (
    ProductCreate, ProductResponse, ProductUpdate, ProductMove)
from app.services.user_service import get_current_user
from typing import List
from app.schemas import utils  


router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    return product_service.create_product(product, db, current_user)


@router.get("", response_model=List[ProductResponse])
@router.get("/", response_model=List[ProductResponse])
def get_products(
    query_params: utils.QueryParams = Depends(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return product_service.get_products(db, query_params)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db),
                current_user: dict = Depends(get_current_user)):
    return product_service.get_product(product_id, db)


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int,
                   product_update: ProductUpdate,
                   db: Session = Depends(get_db),
                   current_user: dict = Depends(get_current_user)):
    return product_service.update_product(product_id, product_update, db,
                                          current_user)


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db),
                   current_user: dict = Depends(get_current_user)):
    return product_service.delete_product(product_id, db)


@router.put("/{product_id}", response_model=ProductResponse)
def put_product(product_id: int, move_data: ProductMove,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return product_service.move_product(
        product_id, move_data, db, current_user)
