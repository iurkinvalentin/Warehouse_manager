from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.data.database import get_db
from app.schemas.warehouse import (
    CategoryCreate, CategoryResponse, CategoryUpdate)
from app.services import category_service
from app.services.user_service import get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return category_service.create_category(category, db)


@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return category_service.get_categories(skip, limit, db)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return category_service.get_category(category_id, db)


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return category_service.update_category(category_id, category_update, db)


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return category_service.delete_category(category_id, db)
