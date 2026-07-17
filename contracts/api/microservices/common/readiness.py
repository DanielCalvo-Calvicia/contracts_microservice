from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True, frozen=True)
class ReadinessRequest:
    component: Optional[str] = None


@dataclass(slots=True, frozen=True)
class ReadinessResponse:
    is_ready: bool
    pending_reason: Optional[str] = None
