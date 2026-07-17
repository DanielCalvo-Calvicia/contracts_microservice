from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

AdaptersTTS = Literal[
    "openai"
]


@dataclass(slots=True, frozen=True)
class InitOutboundRequest:
    session_id: str
    adapter: AdaptersTTS = "openai"

@dataclass(slots=True, frozen=True)
class InitOutboundResponse:
    session_id: str
    adapter_initialized: bool