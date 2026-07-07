from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, Optional

from api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class ReadinessRequestDTO:
    pass


@dataclass(slots=True, frozen=True)
class ReadinessRequest(BaseRequest[ReadinessRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class ReadinessResponseDTO:
    is_ready: bool


@dataclass(slots=True, frozen=True)
class ReadinessResponse(BaseResponse[ReadinessResponseDTO]):
    pass