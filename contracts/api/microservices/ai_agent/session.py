from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from contracts.api.microservices.ai_agent.decision import MotorDirective, RobotContext


@dataclass(slots=True, frozen=True)
class AIAgentStartSessionRequest:
    username: str
    email: Optional[str] = None
    session_name: Optional[str] = None


@dataclass(slots=True, frozen=True)
class AIAgentStartSessionResponse:
    success: bool
    session_id: str = ""
    message: Optional[str] = None
    error_code: Optional[str] = None


@dataclass(slots=True, frozen=True)
class AIAgentEndSessionRequest:
    session_id: str


@dataclass(slots=True, frozen=True)
class AIAgentEndSessionResponse:
    success: bool
    message: Optional[str] = None
    error_code: Optional[str] = None


@dataclass(slots=True, frozen=True)
class AIAgentMessageRequest:
    session_id: str
    message: str
    # Sent to conversation-flow only: what motion-flow decided for this message (see RobotContext).
    robot_context: Optional[RobotContext] = None


@dataclass(slots=True, frozen=True)
class AIAgentMessageResponse:
    """What Brain reads back from ``POST /session/message``.

    ``response`` is always the spoken reply (an apology when ``success`` is false).
    ``directive`` is set only when the plan included a physical arm movement; Brain decides
    what to do with it (e.g. call stepper) and always speaks ``response`` regardless.
    """

    success: bool
    response: str = ""
    directive: Optional[MotorDirective] = None
    message: Optional[str] = None
    error_code: Optional[str] = None
