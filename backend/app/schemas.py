"""Pydantic 数据模型。"""
from typing import List, Optional

from pydantic import BaseModel


class ImportErrorItem(BaseModel):
    line: int
    reason: str


class ImportResult(BaseModel):
    success: bool
    message: str
    row_count: int = 0
    regions: List[str] = []
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    errors: List[ImportErrorItem] = []


class AnomalyItem(BaseModel):
    year: int
    month: int
    region: str
    monthly_avg_temp: float
    anomaly: float
    is_anomaly: Optional[bool] = None


class AnomalyResponse(BaseModel):
    items: List[AnomalyItem] = []