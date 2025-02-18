import os
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.user import User
from app.models.warehouse import (
    Warehouse, Category,
    Product, Attribute)
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

POSTGRES_SUPERUSER = os.getenv("POSTGRES_SUPERUSER", "postgres")
POSTGRES_SUPERUSER_PASSWORD = os.getenv("POSTGRES_SUPERUSER_PASSWORD")

CONN_STRING = f"postgresql://{POSTGRES_SUPERUSER}:{POSTGRES_SUPERUSER_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"


def init_db():
    try:
        conn = psycopg2.connect(CONN_STRING)
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute(f"SELECT 1 FROM pg_roles WHERE rolname='{DB_USER}';")
        user_exists = cursor.fetchone()

        if not user_exists:
            cursor.execute(f"CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}';")
            print(f"✅ Создан пользователь {DB_USER}")

        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}';")
        db_exists = cursor.fetchone()

        if not db_exists:
            cursor.execute(f"CREATE DATABASE {DB_NAME} OWNER {DB_USER};")
            print(f"✅ Создана база данных {DB_NAME}")

        cursor.execute(f"ALTER ROLE {DB_USER} SET client_encoding TO 'utf8';")
        cursor.execute(f"ALTER ROLE {DB_USER} SET default_transaction_isolation TO 'read committed';")
        cursor.execute(f"ALTER ROLE {DB_USER} SET timezone TO 'UTC';")
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER};")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")


init_db()

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
