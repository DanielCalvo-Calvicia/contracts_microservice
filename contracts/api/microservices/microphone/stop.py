from __future__ import annotations

from dataclasses import dataclass

from contracts.api.common.session import SessionCloseRequest, SessionCloseResponse


@dataclass(slots=True, frozen=True)
class MicrophoneStopSessionRequest(SessionCloseRequest):
    pass


@dataclass(slots=True, frozen=True)
class MicrophoneStopSessionResponse(SessionCloseResponse):
    pass
