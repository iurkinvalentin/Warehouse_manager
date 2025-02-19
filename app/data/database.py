import os
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

POSTGRES_SUPERUSER = os.getenv("POSTGRES_SUPERUSER", "postgres")
POSTGRES_SUPERUSER_PASSWORD = os.getenv("POSTGRES_SUPERUSER_PASSWORD")

# Подключение суперпользователя для создания БД
SUPERUSER_CONN_STRING = f"postgresql://{POSTGRES_SUPERUSER}:{POSTGRES_SUPERUSER_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"

# Подключение к основной БД
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def init_db():
    """Создает пользователя и базу данных, если они не существуют."""
    try:
        conn = psycopg2.connect(SUPERUSER_CONN_STRING)
        conn.autocommit = True
        cursor = conn.cursor()

        # Проверяем, существует ли пользователь
        cursor.execute(f"SELECT 1 FROM pg_roles WHERE rolname='{DB_USER}';")
        if not cursor.fetchone():
            cursor.execute(f"CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}';")
            print(f"✅ Создан пользователь {DB_USER}")

        # Проверяем, существует ли база данных
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}';")
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {DB_NAME} OWNER {DB_USER};")
            print(f"✅ Создана база данных {DB_NAME}")

        # Настройки пользователя
        cursor.execute(f"ALTER ROLE {DB_USER} SET client_encoding TO 'utf8';")
        cursor.execute(f"ALTER ROLE {DB_USER} SET default_transaction_isolation TO 'read committed';")
        cursor.execute(f"ALTER ROLE {DB_USER} SET timezone TO 'UTC';")
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER};")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")


# Если база не создана, создаем её
if __name__ == "__main__":
    init_db()

# Подключение к SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)





def get_db():
    """Получение сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
