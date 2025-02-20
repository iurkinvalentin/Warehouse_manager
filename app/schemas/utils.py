import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueryParams(BaseModel):
    """Модель для обработки параметров запроса API."""

    filter: Optional[str] = Field(default=None, alias="filter")
    sort: Optional[str] = Field(default=None, alias="sort")
    range: Optional[str] = Field(default=None, alias="range")

    def parse_sort(self) -> List[Dict[str, str]]:
        """Преобразует `sort` из строки в список"""
        if isinstance(self.sort, str):
            try:
                return json.loads(self.sort)
            except json.JSONDecodeError:
                return []
        return self.sort or []

    def parse_filter(self) -> Dict[str, Any]:
        """Преобразует `filter` из строки в словарь"""
        if isinstance(self.filter, str):
            try:
                return json.loads(self.filter)
            except json.JSONDecodeError:
                return {}
        return self.filter or {}

    def parse_range(self) -> Dict[str, int]:
        """Преобразует `range` из строки в словарь"""
        if isinstance(self.range, str):
            try:
                return json.loads(self.range)
            except json.JSONDecodeError:
                return {}
        return self.range or {}
