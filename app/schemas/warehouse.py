from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class WarehouseCreate(BaseModel):
    """Создание склада"""

    name: str
    address: str
    description: Optional[str] = None
    is_active: Optional[bool] = True

    model_config = ConfigDict(from_attributes=True)


class WarehouseUpdate(BaseModel):
    """Обновление склада"""

    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class WarehouseResponse(BaseModel):
    """Ответ API о складе"""

    id: int
    name: str
    address: str
    description: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(BaseModel):
    """Создание категории"""

    name: str
    is_active: Optional[bool] = True

    model_config = ConfigDict(from_attributes=True)


class CategoryUpdate(BaseModel):
    """Обновление категории"""

    name: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(BaseModel):
    """Ответ API о категории"""

    id: int
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    """Создание товара"""

    name: str
    category_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    quantity: Optional[int] = None
    is_active: Optional[bool] = True

    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    """Обновление товара"""

    name: Optional[str] = None
    category_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    quantity: Optional[int] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class ProductResponse(BaseModel):
    """Ответ API о товаре"""

    id: int
    name: str
    category_id: int
    warehouse_id: int
    quantity: Optional[int] = None
    is_active: Optional[bool] = None
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ProductMove(BaseModel):
    """Перемещение товара между складами"""

    destination_warehouse_id: int


class AttributeCreate(BaseModel):
    """Создание характеристики"""

    name: str
    value: Optional[str] = None
    product_id: int

    model_config = ConfigDict(from_attributes=True)


class AttributeUpdate(BaseModel):
    """Обновление характеристики"""

    name: Optional[str] = None
    value: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AttributeResponse(BaseModel):
    """Ответ API о характеристике"""

    id: int
    name: str
    value: Optional[str] = None
    product_id: int

    model_config = ConfigDict(from_attributes=True)
