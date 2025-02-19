from sqlalchemy.orm import Session
from app.data.database import SessionLocal
from app.models.warehouse import Warehouse, Product, Category, Attribute
from app.models.user import User
from datetime import datetime
from bcrypt import hashpw, gensalt

# Функция для хеширования паролей
def hash_password(password: str) -> str:
    return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")

def seed_database(db: Session):
    """Заполняет базу тестовыми данными"""

    # 🔹 Проверяем, есть ли пользователи
    existing_users = db.query(User).filter(User.username.in_(["ivan.petrov", "anna.sidorova"])).all()
    existing_usernames = {user.username for user in existing_users}

    users = [
        User(username="ivan.petrov", first_name="Иван", last_name="Петров", age=35,
             email="ivan.petrov@example.com", phone="+79161234567",
             hashed_password=hash_password("password123")),

        User(username="anna.sidorova", first_name="Анна", last_name="Сидорова", age=29,
             email="anna.sidorova@example.com", phone="+79261234568",
             hashed_password=hash_password("securepass")),
    ]

    users_to_add = [user for user in users if user.username not in existing_usernames]
    if users_to_add:
        db.add_all(users_to_add)
        db.commit()

    # 🔹 Проверяем, есть ли склады
    if not db.query(Warehouse).count():
        warehouses = [
            Warehouse(name="Склад №1", address="Москва, ул. Ленина, 10", description="Главный склад", is_active=True),
            Warehouse(name="Склад №2", address="Санкт-Петербург, Невский пр., 25", description="Дополнительный склад", is_active=True),
            Warehouse(name="Склад №3", address="Новосибирск, ул. Кирова, 15", description="Запасной склад", is_active=False),
        ]
        db.add_all(warehouses)
        db.commit()

    # 🔹 Проверяем, есть ли категории
    if not db.query(Category).count():
        categories = [
            Category(name="Электроника", is_active=True),
            Category(name="Одежда", is_active=True),
            Category(name="Бытовая техника", is_active=True),
        ]
        db.add_all(categories)
        db.commit()

    # 🔹 Получаем или создаем характеристики
    characteristics = db.query(Attribute).all()

    if not characteristics:
        characteristics = [
            Attribute(name="Цвет", value="Черный"),
            Attribute(name="Мощность", value="1500 Вт"),
            Attribute(name="Материал", value="Кожа"),
        ]
        db.add_all(characteristics)
        db.commit()
        characteristics = db.query(Attribute).all()  # Повторно загружаем характеристики из БД

    # 🔹 Проверяем, есть ли товары
    if not db.query(Product).count():
        products = [
            Product(
                name="Ноутбук Lenovo",
                category_id=1,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                warehouse_id=1,
                quantity=10,
                is_active=True,
                attributes=[characteristics[0], characteristics[1]],  # ✅ Теперь characteristics определена всегда
                created_by=1,
                updated_by=1,
            ),
            Product(
                name="Куртка зимняя",
                category_id=2,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                warehouse_id=2,
                quantity=5,
                is_active=True,
                attributes=[characteristics[2]],  # ✅ Теперь characteristics определена всегда
                created_by=2,
                updated_by=2,
            ),
        ]
        db.add_all(products)
        db.commit()

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db)
        print("✅ База данных успешно заполнена тестовыми данными!")
    finally:
        db.close()


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db)
        print("✅ База данных успешно заполнена тестовыми данными!")
    finally:
        db.close()
