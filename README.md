# Система управления складами

## Описание
**warehouse_manager** — это API для управления складскими запасами, товарами, категориями и пользователями. Поддерживается авторизация через OAuth2 с JWT, работа с базой данных PostgreSQL, миграции Alembic и тестирование с Pytest.

### Возможности
- Управление товарами: добавление, редактирование, удаление
- Управление складами: создание, обновление, удаление складов
- Категоризация товаров
- Атрибуты товаров
- Авторизация и аутентификация пользователей (OAuth2 + JWT)
- Гибкая система фильтрации, сортировки и пагинации
- Поддержка миграций базы данных через Alembic
- API-документация через Swagger и ReDoc

## Стек технологий
- **FastAPI** — асинхронный веб-фреймворк на Python
- **PostgreSQL** — реляционная база данных
- **SQLAlchemy** — ORM для работы с базой данных
- **Pydantic** — валидация данных
- **OAuth2 + JWT** — система авторизации
- **Pytest** — тестирование
- **Uvicorn** — ASGI сервер для запуска приложения
- **Alembic** — миграции базы данных

## Установка и запуск проекта
### 1. Клонирование репозитория
```bash
git clone https://github.com/yourusername/warehouse_manager.git
cd warehouse_manager
```

### 2. Создание виртуального окружения и установка зависимостей
```bash
python -m venv venv
source venv/bin/activate  # для Linux/macOS
venv\Scripts\activate    # для Windows
pip install -r requirements.txt
```

### 3. Настройка переменных окружения
Создайте файл `.env` в корневой директории и добавьте туда переменные:
```env
DB_NAME=warehouse_db
DB_USER=warehouse_user
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
POSTGRES_SUPERUSER=postgres
POSTGRES_SUPERUSER_PASSWORD=your_superuser_password
SECRET_KEY=your_secret_key
```

### 4. Запуск базы данных (если используется Docker)
```bash
docker-compose up -d
```

### 5. Применение миграций
```bash
alembic upgrade head
```

### 6. Запуск приложения
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Приложение будет доступно по адресу: [http://localhost:8000](http://localhost:8000)

### 7. Документация API
После запуска проекта API-документация доступна по адресам:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Тестирование
Для запуска тестов используйте команду:
```bash
pytest
```

