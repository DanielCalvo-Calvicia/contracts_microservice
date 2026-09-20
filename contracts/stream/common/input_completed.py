from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class InputCompletedEventDTO:
    """How the upload ended: ``end_of_input`` (the sender closed its stream cleanly)."""

    reason: str = "end_of_input"


@dataclass(frozen=True, slots=True)
class InputCompletedEvent(BaseEvent[InputCompletedEventDTO]):
    """Answer to an upload request: every event of the sender's stream has been consumed.

    It acknowledges the *request*, so it can never be mistaken for content (a transcript or audio,
    which end with ``completed``).
    """

    type: Literal[EventType.INPUT_COMPLETED] = field(
        default=EventType.INPUT_COMPLETED,
        init=False,
    )
