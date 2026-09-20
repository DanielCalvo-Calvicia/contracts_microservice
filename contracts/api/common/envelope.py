"""The JSON envelope every microservice answers its non-stream HTTP endpoints with.

    {"action": "start_stream", "status": "success", "status_code": 200,
     "message": "...", "timestamp": 1758380000.0, "data": <contract dataclass as an object>}

``data`` is the contract dataclass of that endpoint (see ``contracts.api.microservices``),
serialized as a plain object; failures carry the error text. Stream bodies (``contracts.stream``)
are not wrapped in it.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Generic, Literal, TypeVar

T = TypeVar("T")

EnvelopeStatus = Literal["success", "accepted", "error"]


@dataclass(slots=True, frozen=True)
class ApiEnvelope(Generic[T]):
    action: str
    status: EnvelopeStatus
    status_code: int
    message: str
    data: T | None = None
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def success(
        cls, action: str, message: str, data: T | None = None, *, status_code: int = 200
    ) -> ApiEnvelope[T]:
        return cls(action, "success", status_code, message, data)

    @classmethod
    def accepted(
        cls, action: str, message: str, data: T | None = None, *, status_code: int = 202
    ) -> ApiEnvelope[T]:
        return cls(action, "accepted", status_code, message, data)

    @classmethod
    def failure(
        cls, action: str, message: str, status_code: int, data: Any = None  # noqa: ANN401
    ) -> ApiEnvelope[Any]:
        return cls(action, "error", status_code, message, data)

    def to_dict(self) -> dict[str, Any]:
        data = self.data
        if is_dataclass(data) and not isinstance(data, type):
            data = asdict(data)
        return {
            "action": self.action,
            "status": self.status,
            "status_code": self.status_code,
            "message": self.message,
            "timestamp": self.timestamp,
            "data": data,
        }
