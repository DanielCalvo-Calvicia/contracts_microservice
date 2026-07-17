from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncIterable, Literal, Protocol

ByteStream = AsyncIterable[bytes]
TextStream = AsyncIterable[str]

StreamDirection = Literal["inbound", "outbound"]


@dataclass(slots=True, frozen=True)
class StreamBinding:
    session_id: str
    direction: StreamDirection


class ByteStreamProcessor(Protocol):
    async def process(self, stream: ByteStream) -> None:
        ...
