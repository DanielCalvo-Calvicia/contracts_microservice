from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, Optional

from api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class MicrophoneStopRequestDTO:
    pass


@dataclass(slots=True, frozen=True)
class MicrophoneStopRequest(BaseRequest[MicrophoneStopRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class MicrophoneStopResponseDTO:
    success: bool = True


@dataclass(slots=True, frozen=True)
class MicrophoneStopResponse(BaseResponse[MicrophoneStopResponseDTO]):
    pass