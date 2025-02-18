from sqlalchemy.orm import Query, Session
from sqlalchemy import and_, or_
from typing import Dict, Any, List, Type
from app.services.utils import QueryParams


def apply_filters(query: Query, model, filters: Dict[str, Any]) -> Query:
    """Применяет фильтры к SQLAlchemy-запросу"""
    if not filters:
        return query

    for field, condition in filters.items():
        column = getattr(model, field, None)
        if not column:
            continue  # Пропускаем, если такого поля нет в модели

        for operator, value in condition.items():
            if operator == "NOT":
                query = query.filter(column != value)
            elif operator == "ILIKE":
                query = query.filter(column.ilike(f"%{value}%"))
            elif operator == "EQUAL":
                query = query.filter(column == value)
            elif operator == "IN":
                query = query.filter(column.in_(value))
            elif operator == "NOT IN":
                query = query.filter(~column.in_(value))
            elif operator in ["GE", "GTE"]:
                query = query.filter(column >= value)
            elif operator in ["LE", "LTE"]:
                query = query.filter(column <= value)
            elif operator == "BETWEEN":
                query = query.filter(column.between(value[0], value[1]))

    return query


def apply_sorting(query: Query, model, sorting: List[Dict[str, str]]) -> Query:
    """Применяет сортировку к SQLAlchemy-запросу"""
    if not sorting:
        return query

    for sort_param in sorting:
        field = sort_param["field"]
        order = sort_param["order"].upper()
        column = getattr(model, field, None)
        if not column:
            continue
        if order == "ASC":
            query = query.order_by(column.asc())
        elif order == "DESC":
            query = query.order_by(column.desc())

    return query


def apply_range(query: Query, range_params: Dict[str, int]) -> Query:
    """Применяет `limit` и `offset` к SQLAlchemy-запросу"""
    if not range_params:
        return query

    limit = range_params.get("limit")
    offset = range_params.get("offset")

    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)

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
