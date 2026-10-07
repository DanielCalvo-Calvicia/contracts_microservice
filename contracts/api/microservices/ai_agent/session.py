from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from contracts.api.microservices.ai_agent.decision import AgentFlowName, MotorDirective


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
    # Whether the movement flow words a short spoken line ("Turning my left arm 90 degrees") besides moving.
    # Brain sets it from its own settings. When false, only a refusal or a question is spoken.
    speak_movements: bool = True


@dataclass(slots=True, frozen=True)
class AIAgentMessageResponse:
    """What Brain reads back from ``POST /session/message``.

    ai-agent identifies the message first and then runs exactly one flow (``flow``).
    ``response`` is the spoken reply (an apology when ``success`` is false). It can be empty: a movement
    that is not to be spoken (see ``AIAgentMessageRequest.speak_movements``).
    ``directives`` is the movement sequence to run, in order (for example left 90, then left -90), empty when
    nothing is to be moved. Brain runs it as a whole or not at all, and is the only service that acts on it.
    ``awaiting_user_input`` is true when ``response`` is a question: the flow is paused and the next message of
    the session is its answer (ai-agent resumes that flow without identifying the message again).
    """

    success: bool
    response: str = ""
    message: Optional[str] = None
    error_code: Optional[str] = None
    directives: tuple[MotorDirective, ...] = ()
    awaiting_user_input: bool = False
    flow: Optional[AgentFlowName] = None
