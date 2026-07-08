from __future__ import annotations

from dataclasses import dataclass

from contracts.api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class HealthCheckRequestDTO:
    pass


@dataclass(slots=True, frozen=True)
class HealthCheckRequest(BaseRequest[HealthCheckRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class HealthCheckResponseDTO:
    pass

@dataclass(slots=True, frozen=True)
class HealthCheckResponse(BaseResponse[HealthCheckResponseDTO]):
    pass
