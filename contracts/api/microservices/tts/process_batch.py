from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True, frozen=True)
class ProcessBatchRequest:
    """``POST /process/batch``: one complete text, spoken in the requested PCM16 format."""

    text: str
    sample_rate: int = 22050
    channels: int = 1
    session_id: Optional[str] = None


@dataclass(slots=True, frozen=True)
class ProcessBatchResponse:
    """``data`` of ``POST /process/batch``: the whole utterance as base64 PCM16."""

    audio_data_base64: str
    sample_rate: int
    channels: int
