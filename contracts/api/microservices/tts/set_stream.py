from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncIterable, Literal, Optional

from contracts.stream.common.base import BaseEvent

@dataclass(slots=True, frozen=True)
class SetStreamRequest:
    stream: AsyncIterable[BaseEvent]