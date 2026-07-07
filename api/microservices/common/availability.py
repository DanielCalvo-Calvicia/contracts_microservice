from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, Optional

from api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class AvailabilityRequestDTO:
    pass


@dataclass(slots=True, frozen=True)
class AvailabilityRequest(BaseRequest[AvailabilityRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class AvailabilityResponseDTO:
    is_available: bool


@dataclass(slots=True, frozen=True)
class AvailabilityResponse(BaseResponse[AvailabilityResponseDTO]):
    pass