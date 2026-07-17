from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True, frozen=True)
class STTProcessBatchRequest:
    audio_data: bytes
    sample_rate: int = 16000
    language: Optional[str] = None
    model: Optional[str] = None


@dataclass(slots=True, frozen=True)
class STTProcessBatchResponse:
    text: str
    confidence: Optional[float] = None
