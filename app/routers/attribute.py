from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.data.database import get_db
from app.services import attribute_service
from app.schemas.warehouse import (
    AttributeCreate, AttributeResponse, AttributeUpdate)
from app.services.user_service import get_current_user
from typing import List


router = APIRouter(prefix="/attributes", tags=["Attributes"])


@router.post("/", response_model=AttributeResponse)
def create_attribute(attribute: AttributeCreate,
                     db: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user)):
    return attribute_service.create_attribute(attribute, db)


@router.get("/", response_model=List[AttributeResponse])
def get_attributes(skip: int = 0,
                   limit: int = 100, db: Session = Depends(get_db),
                   current_user: dict = Depends(get_current_user)):
    return attribute_service.get_attributes(skip, limit, db)


@router.get("/{attribute_id}", response_model=AttributeResponse)
def get_attribute(attribute_id: int, db: Session = Depends(get_db),
                  current_user: dict = Depends(get_current_user)):
    return attribute_service.get_attribute(attribute_id, db)


@router.patch("/{attribute_id}", response_model=AttributeResponse)
def update_attribute(attribute_id: int,
                     attribute_update: AttributeUpdate,
                     db: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user)):
    return attribute_service.update_attribute(attribute_id,
                                              attribute_update, db)


@router.delete("/{attribute_id}")
def delete_attribute(attribute_id: int, db: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user)):
    return attribute_service.delete_attribute(attribute_id, db)
