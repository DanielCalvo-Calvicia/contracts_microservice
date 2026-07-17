from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class HealthCheckRequest:
    pass


@dataclass(slots=True, frozen=True)
class HealthCheckResponse:
    healthy: bool
