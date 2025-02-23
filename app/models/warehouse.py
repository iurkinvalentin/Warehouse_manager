from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Warehouse(Base):
    """Склад"""

    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    address = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    products = relationship(
        "Product", backref="warehouse", cascade="all, delete-orphan"
    )


class Category(Base):
    """Категория товара"""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)

    products = relationship(
        "Product", backref="category", cascade="all, delete-orphan")


class Product(Base):
    """Товар"""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    quantity = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    attributes = relationship(
        "Attribute", backref="product", cascade="all, delete-orphan"
    )


class Attribute(Base):
    """Характеристика товара"""

    __tablename__ = "attributes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    value = Column(String, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
