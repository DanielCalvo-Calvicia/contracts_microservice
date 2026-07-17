from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncIterable

from contracts.stream.common.base import BaseEvent

@dataclass(slots=True, frozen=True)
class GetStreamRequest:
    session_id: str

@dataclass(slots=True, frozen=True)
class GetStreamResponse:
    stream: AsyncIterable[BaseEvent]