from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, Optional

from contracts.api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class HealthCheckRequestDTO:
    pass


@dataclass(slots=True, frozen=True)
class HealthCheckRequest(BaseRequest[HealthCheckRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class HealthCheckResponseDTO:
    is_available: bool


@dataclass(slots=True, frozen=True)
class HealthCheckResponse(BaseResponse[HealthCheckResponseDTO]):
    pass
