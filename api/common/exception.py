from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")

@dataclass(slots=True, frozen=True)
class ExceptionApiResponse(Generic[T]):
    status_code: int
    detail: str
    headers: Optional[dict[str, str]]
    action: str
    status: str
    message: str
    timestamp: float
    metadata: Optional[dict[str, Any]]
    data: Optional[T]


