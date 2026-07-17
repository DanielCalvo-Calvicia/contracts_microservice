from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

@dataclass(slots=True, frozen=True)
class ProcessBatchRequest:
    session_id: str
    text: str