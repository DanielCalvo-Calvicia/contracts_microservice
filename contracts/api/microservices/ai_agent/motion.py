from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from contracts.api.microservices.ai_agent.decision import MotorDirective


@dataclass(slots=True, frozen=True)
class AIAgentMotionMessageResponse:
    """What Brain reads back from ``POST /motion-flow/session/message``.

    ``directives`` is the movement sequence to run, in order (for example left 90, then left -90).
    It is empty when nothing is to be moved: the request was not a movement, it was rejected
    (``response`` then says why, and is always safe to speak) or motion-flow is asking the user for a missing
    detail (``awaiting_user_input``; ``response`` is then the question, to speak as it is). Brain runs the
    sequence as a whole or not at all.
    The session start and end routes of motion-flow answer with the same shapes as conversation-flow's
    (``AIAgentStartSessionResponse``, ``AIAgentEndSessionResponse``).
    """

    success: bool
    response: str = ""
    directives: tuple[MotorDirective, ...] = ()
    awaiting_user_input: bool = False
    message: Optional[str] = None
    error_code: Optional[str] = None
