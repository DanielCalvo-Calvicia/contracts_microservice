from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")


@dataclass(slots=True, frozen=True)
class Command(Generic[T]):
    """Application input contract with optional metadata for tracing/correlation."""

    data: T
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class Result(Generic[T]):
    """Application output contract without transport concerns."""

    ok: bool
    message: str
    data: Optional[T] = None
    error_code: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
