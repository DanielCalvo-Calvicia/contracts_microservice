from __future__ import annotations

from dataclasses import dataclass

from stream.common.base import BaseEvent


@dataclass(slots=True, frozen=True)
class MicrophoneCompletedOutboundEventDTO:
    reason: str
    output_bytes_base64: str

@dataclass(slots=True, frozen=True)
class MicrophoneCompletedOutboundEvent(BaseEvent[MicrophoneCompletedOutboundEventDTO]):
    type: str = "completed"

