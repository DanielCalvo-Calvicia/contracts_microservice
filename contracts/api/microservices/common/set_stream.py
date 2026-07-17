from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncIterable, Literal, Optional

from contracts.stream.common.base import BaseEvent

@dataclass(slots=True, frozen=True)
class SetStreamRequest:
    session_id: str
    stream: AsyncIterable[BaseEvent]

@dataclass(slots=True, frozen=True)
class SetStreamResponse:
    success: bool
    message: Optional[str]


