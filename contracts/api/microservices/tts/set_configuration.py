from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

OpenAITTSVoice = Literal[
    "alloy",
    "ash",
    "ballad",
    "coral",
    "echo",
    "fable",
    "nova",
    "onyx",
    "sage",
    "shimmer",
]

OpenAITTSModel = Literal[
    "gpt-4o-mini-tts",
    "tts-1",
    "tts-1-hd",
]

OpenAITTSResponseFormat = Literal[
    "wav",
    "mp3",
]

@dataclass(slots=True, frozen=True)
class SetConfigurationRequest:
    session_id: str
    speech_rate: int = 140
    voice: OpenAITTSVoice = "alloy"
    model: OpenAITTSModel = "gpt-4o-mini-tts"
    response_format: OpenAITTSResponseFormat = "wav"
    instructions: Optional[str] = None
    speed: Optional[float] = None



@dataclass(slots=True, frozen=True)
class TTSGetStreamResponse:
    session_id: str
    stream_ready: bool
    media_type: str = "audio/L16"
    message: str = "ready"
