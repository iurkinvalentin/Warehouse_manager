from fastapi import Query
from typing import Dict, Any, List, Optional


class QueryParams:
    """Универсальный класс для обработки `filter`, `sort`, `range`"""
    
    def __init__(
        self,
        filter: Optional[Dict[str, Any]] = Query(None),
        sort: Optional[List[Dict[str, str]]] = Query(None),
        range: Optional[Dict[str, int]] = Query(None),
    ):
        self.filter = filter or {}
        self.sort = sort or []
        self.range = range or {}
