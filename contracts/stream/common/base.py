from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class BaseEvent(Generic[T]):
    type: str
    sequence: int
    timestamp: str
    payload: T



