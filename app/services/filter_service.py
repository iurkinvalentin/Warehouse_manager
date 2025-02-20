from typing import Any, Dict, List, Type
from sqlalchemy.orm import Query, Session

from app.schemas.utils import QueryParams

DEFAULT_LIMIT = 100


def apply_filters(query: Query, model, filters: Dict[str, Any]) -> Query:
    """Применяет фильтры к SQLAlchemy-запросу"""
    if not filters:
        return query

    for field, condition in filters.items():
        column = getattr(model, field, None)
        if not column:
            raise ValueError(
                f"Field '{field}' not found in model {model.__name__}")

        for operator, value in condition.items():
            if operator == "NOT":
                query = query.filter(column != value)
            elif operator == "ILIKE":
                query = query.filter(column.ilike(f"%{value}%"))
            elif operator == "EQUAL":
                query = query.filter(column == value)
            elif operator == "IN":
                if not isinstance(value, list):
                    raise ValueError(
                        f"Value for IN must be a list, got {type(value)}")
                query = query.filter(column.in_(value))
            elif operator == "NOT IN":
                if not isinstance(value, list):
                    raise ValueError(
                        f"Value for NOT IN must be a list, got {type(value)}"
                    )
                query = query.filter(~column.in_(value))
            elif operator in ["GE", "GTE"]:
                query = query.filter(column >= value)
            elif operator in ["LE", "LTE"]:
                query = query.filter(column <= value)
            elif operator == "BETWEEN":
                if not isinstance(value, list) or len(value) != 2:
                    raise ValueError("BETWEEN must be a list with two values")
                query = query.filter(column.between(value[0], value[1]))

    return query


def apply_sorting(query: Query, model, sorting: List[Dict[str, str]]) -> Query:
    """Применяет сортировку к SQLAlchemy-запросу"""
    if not sorting:
        print("⚠️ Нет параметров сортировки!")
        return query

    print(f"🛠 Применяем сортировку: {sorting}")

    order_by_clauses = []

    for sort_param in sorting:
        field = sort_param.get("field")
        order = sort_param.get("order", "ASC").upper()

        if not field:
            raise ValueError(" Поле `field` обязательно для сортировки!")

        column = getattr(model, field, None)
        if not column:
            raise ValueError(
                f" Поле `{field}` не найдено в модели `{model.__name__}`")

        if order not in ["ASC", "DESC"]:
            raise ValueError(
                f" Неверное значение `order`: "
                f"{order}. Ожидается 'ASC' или 'DESC'."
            )

        order_by_clauses.append(
            column.asc() if order == "ASC" else column.desc())

    query = query.order_by(*order_by_clauses)

    print(f"✅ Итоговый SQL-запрос с сортировкой: {str(query)}")
    return query


def apply_range(query: Query, range_params: Dict[str, int]) -> Query:
    if not range_params:
        return query

    limit = range_params.get("limit", DEFAULT_LIMIT)
    offset = range_params.get("offset", 0)

    query = query.offset(offset).limit(limit)
    return query


def get_filtered_data(
    db: Session,
    model: Type,
    query_params: QueryParams,
) -> List:
    """Применяет фильтрацию, сортировку и пагинацию к модели"""
    query = db.query(model)

    query = apply_filters(query, model, query_params.filter)
    query = apply_sorting(query, model, query_params.sort)
    query = apply_range(query, query_params.range)

    return query.all()
