from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import json


class QueryParams(BaseModel):
    filter: Optional[str] = Field(default=None, alias="filter")
    sort: Optional[str] = Field(default=None, alias="sort")
    range: Optional[str] = Field(default=None, alias="range")  # ✅ Теперь `range` как строка

    def parse_sort(self) -> List[Dict[str, str]]:
        """Преобразует `sort` из строки в список"""
        if isinstance(self.sort, str):
            try:
                return json.loads(self.sort)  # ✅ Преобразуем JSON-строку в Python-список
            except json.JSONDecodeError:
                return []
        return self.sort or []
    
    def parse_filter(self) -> Dict[str, Any]:
        """Преобразует `filter` из строки в словарь"""
        if isinstance(self.filter, str):
            try:
                return json.loads(self.filter)  # ✅ Преобразуем JSON-строку в словарь
            except json.JSONDecodeError:
                return {}
        return self.filter or {}

    def parse_range(self) -> Dict[str, int]:
        """Преобразует `range` из строки в словарь"""
        if isinstance(self.range, str):
            try:
                return json.loads(self.range)  # ✅ Преобразуем JSON-строку в словарь
            except json.JSONDecodeError:
                return {}
        return self.range or {}
