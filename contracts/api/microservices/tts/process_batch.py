from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True, frozen=True)
class TTSProcessBatchRequest:
    text: str
    sample_rate: int = 22050
    channels: int = 1
    language: Optional[str] = None
    voice: Optional[str] = None
    model: Optional[str] = None


@dataclass(slots=True, frozen=True)
class TTSProcessBatchResponse:
    audio_data_base64: str
    sample_rate: int
    channels: int
