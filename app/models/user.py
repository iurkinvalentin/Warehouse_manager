from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    """Пользователь"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)

    created_products = relationship(
        "Product",
        backref="creator",
        foreign_keys="[Product.created_by]",
        cascade="all, delete-orphan",
    )

    updated_products = relationship(
        "Product",
        backref="updator",
        foreign_keys="[Product.updated_by]",
        cascade="all, delete-orphan",
    )
