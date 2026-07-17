from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar
from enum import StrEnum

T = TypeVar("T")


class EventType(StrEnum):
    HEARTBEAT = "heartbeat"
    START_STREAM = "stream_started"
    PARTIAL = "partial"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class BaseEvent(Generic[T]):
    type: EventType
    sequence: int
    timestamp: datetime
    payload: T



