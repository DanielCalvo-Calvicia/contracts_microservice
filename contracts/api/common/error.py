from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(slots=True, frozen=True)
class ErrorDetails:
    code: str
    message: str
    retryable: bool = False
    details: Optional[dict[str, Any]] = None


@dataclass(slots=True, frozen=True)
class ErrorResult:
    error: ErrorDetails
    context: dict[str, Any] = field(default_factory=dict)
