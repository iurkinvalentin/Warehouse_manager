from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.data.database import get_db
from app.services import warehouse_service
from app.schemas.warehouse import (
    WarehouseCreate, WarehouseResponse, WarehouseUpdate)
from app.services.user_service import get_current_user
from typing import List


router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.post("/", response_model=WarehouseResponse)
def create_warehouse(warehouse: WarehouseCreate,
                     db: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user)):
    return warehouse_service.create_warehouse(warehouse, db)


@router.get("/", response_model=List[WarehouseResponse])
def get_warehouses(skip: int = 0,
                   limit: int = 100, db: Session = Depends(get_db),
                   current_user: dict = Depends(get_current_user)):
    return warehouse_service.get_warehouses(skip, limit, db)


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
def get_warehouse(warehouse_id: int, db: Session = Depends(get_db),
                  current_user: dict = Depends(get_current_user)):
    return warehouse_service.get_warehouse(warehouse_id, db)


@router.patch("/{warehouse_id}", response_model=WarehouseResponse)
def update_warehouse(warehouse_id: int,
                     warehouse_update: WarehouseUpdate,
                     db: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user)):
    return warehouse_service.update_warehouse(warehouse_id,
                                              warehouse_update, db)


@router.delete("/{warehouse_id}")
def delete_warehouse(warehouse_id: int, db: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user)):
    return warehouse_service.delete_warehouse(warehouse_id, db)
