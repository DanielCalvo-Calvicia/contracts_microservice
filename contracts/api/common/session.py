from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Literal, Optional, TypeVar

ConfigT = TypeVar("ConfigT")

SessionState = Literal["created", "active", "closing", "closed", "failed"]


@dataclass(slots=True, frozen=True)
class SessionCreateRequest(Generic[ConfigT]):
    config: ConfigT
    client_id: Optional[str] = None
    correlation_id: Optional[str] = None


@dataclass(slots=True, frozen=True)
class SessionCreateResponse:
    session_id: str
    state: SessionState
    created_at: float


@dataclass(slots=True, frozen=True)
class SessionStatusRequest:
    session_id: str


@dataclass(slots=True, frozen=True)
class SessionStatusResponse:
    session_id: str
    state: SessionState
    updated_at: float


@dataclass(slots=True, frozen=True)
class SessionCloseRequest:
    session_id: str
    reason: Optional[str] = None


@dataclass(slots=True, frozen=True)
class SessionCloseResponse:
    session_id: str
    closed: bool
    closed_at: float
