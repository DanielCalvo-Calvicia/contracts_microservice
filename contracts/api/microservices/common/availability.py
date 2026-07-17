from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True, frozen=True)
class AvailabilityRequest:
    service_name: Optional[str] = None


@dataclass(slots=True, frozen=True)
class AvailabilityResponse:
    is_available: bool
    reason: Optional[str] = None
