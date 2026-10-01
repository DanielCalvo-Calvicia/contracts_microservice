"""Brain <-> ai-agent over real HTTP: does Brain understand ai-agent's flows (conversation-flow, motion-flow)?

A real ai-agent process (its own virtualenv and REAL composition root: flows, routes, sessions, tracing; only
the LLM is replaced by a keyword script, see ``fake_services.build_ai_agent``) is driven by Brain's real
composition root: its real config defaults, real adapters and real ``BrainService.decide``. Only the stepper is
a recorder (its wire is covered by Brain's own tests). The assertions are on what Brain decides to say and move,
and on which flows ai-agent really ran.

Run it with the Brain virtualenv from the workspace root:

    brain_microservice/windows/Scripts/python.exe -m pytest contracts/tests/e2e/test_brain_ai_agent_flows.py -q

Skipped when ai-agent's virtualenv is missing. Set ``RUN_E2E=0`` to skip it explicitly.
"""

import asyncio
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

REPO = Path(__file__).resolve().parents[3]
FAKE_SERVICES = Path(__file__).with_name("fake_services.py")
AI_AGENT_DIR = REPO / "ai-agent"
AI_AGENT_PYTHON = AI_AGENT_DIR / "windows" / "Scripts" / "python.exe"

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_E2E") == "0" or not AI_AGENT_PYTHON.exists(),
    reason="needs ai-agent's virtualenv",
)

PLANNER = "motion_planner_phase20_response_format"
PROJECT_MANAGER = "project_manager_phase2_response_format"
DRAFT = "draft_writer_phase7_response_format"


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class AIAgentProcess:
    def __init__(self) -> None:
        self.port = _free_port()
        self.base_url = f"http://127.0.0.1:{self.port}"
        self.proc: subprocess.Popen | None = None

    def start(self) -> None:
        self.proc = subprocess.Popen(
            [str(AI_AGENT_PYTHON), str(FAKE_SERVICES), "ai_agent", str(self.port)],
            cwd=AI_AGENT_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        deadline = time.monotonic() + 90
        while True:
            try:
                if httpx.get(f"{self.base_url}/health", timeout=2).status_code == 200:
                    return
            except httpx.HTTPError:
                pass
            if self.proc.poll() is not None:
                raise AssertionError("ai-agent exited: " + self.proc.stderr.read().decode(errors="replace")[-2000:])
            assert time.monotonic() < deadline, "ai-agent did not start"
            time.sleep(0.3)

    def stop(self) -> None:
        if self.proc is None:
            return
        self.proc.terminate()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        self.proc = None

    def restart(self) -> None:
        self.stop()
        self.start()

    def formats(self) -> list[str]:
        """The LLM calls (so: the phases of the flows) ai-agent made since the last reset."""
        return httpx.get(f"{self.base_url}/_e2e/formats", timeout=5).json()

    def reset(self) -> None:
        httpx.get(f"{self.base_url}/_e2e/reset", timeout=5)


@pytest.fixture(scope="module")
def agent():
    process = AIAgentProcess()
    process.start()
    try:
        yield process
    finally:
        process.stop()


class RecordingStepper:
    """Brain is the only one that moves anything: this records what it would send to the stepper, in order."""

    def __init__(self) -> None:
        self.moves = []

    async def move(self, directive):
        from application.dtos.outbound_dtos import StepperMoveResponseDto

        self.moves.append(directive)
        return StepperMoveResponseDto(success=True, message="moved")


def with_brain(agent: AIAgentProcess, scenario):
    """Runs ``scenario(service, stepper)`` with Brain built by its REAL composition root against this ai-agent."""
    brain_dir = str(REPO / "brain_microservice")
    if brain_dir not in sys.path:
        sys.path.insert(0, brain_dir)
    os.environ["AI_AGENT_BASE_URL"] = agent.base_url
    from composition_root.config import load_config
    from composition_root.dependencies.brain_dependency import generate_brain_core_dependency

    agent.reset()

    async def main():
        core = generate_brain_core_dependency(load_config())  # Brain's own defaults for every ai-agent route
        stepper = RecordingStepper()
        core.service.stepper_port = stepper
        try:
            return await scenario(core.service, stepper)
        finally:
            for adapter in (core.microphone_adapter, core.stt_adapter, core.tts_adapter, core.speaker_adapter,
                            *core.agent_flow_adapters, core.stepper_adapter):
                await adapter.close()

    return asyncio.run(main())


def directive(arm: str, degrees: float, direction: str):
    from application.dtos.outbound_dtos import MotorDirectiveDto

    return MotorDirectiveDto(arm=arm, degrees=degrees, direction=direction)


# ------------------------------------------------------------------ the flows, as Brain sees them
# Brain asks them one after the other, in order: conversation-flow writes the reply (what the user hears),
# motion-flow, only when conversation-flow has ended, decides the movements.


def test_a_plain_message_runs_conversation_flow_then_motion_flow_and_moves_nothing(agent):
    async def scenario(service, stepper):
        return await service.decide("hello there")

    decision = with_brain(agent, scenario)

    assert decision.spoken == ("PLAIN",)                  # conversation-flow answered; motion-flow had nothing to say
    assert decision.directives == () and decision.failed_flows == ()
    formats = agent.formats()
    assert DRAFT in formats and PLANNER in formats
    assert formats.index(DRAFT) < formats.index(PLANNER)  # motion-flow was asked only after conversation-flow ended


def test_a_movement_sequence_is_understood_ordered_and_run_after_the_reply(agent):
    async def scenario(service, stepper):
        decision = await service.decide("raise your left arm there and back")
        await service.move_arms(decision.directives)
        return decision, stepper.moves

    decision, moves = with_brain(agent, scenario)

    expected = (directive("left", 90.0, "forward"), directive("left", -90.0, "forward"))
    assert decision.directives == expected                # the list, in order, signed degrees intact
    assert tuple(moves) == expected                       # and Brain would send them to the stepper in that order
    assert decision.spoken == ("PLAIN",)                  # the reply is conversation-flow's; motion-flow added no words
    assert PROJECT_MANAGER not in agent.formats()         # nothing was planned: the fast path answered


def test_a_missing_detail_is_asked_after_the_reply_and_the_answer_goes_only_to_motion_flow(agent):
    async def scenario(service, stepper):
        asked = await service.decide("move my arm")
        before_the_answer = len(agent.formats())
        answered = await service.decide("thirty degrees, 30 degrees")
        return asked, agent.formats()[before_the_answer:], answered

    asked, calls_for_the_answer, answered = with_brain(agent, scenario)

    assert asked.spoken == ("PLAIN", "Which arm, and how many degrees?")   # the reply, then motion-flow's question
    assert asked.directives == ()
    assert DRAFT not in calls_for_the_answer                      # the answer was NOT sent to conversation-flow ...
    assert PLANNER in calls_for_the_answer                        # ... only to motion-flow's paused run
    assert answered.directives == (directive("left", 30.0, "forward"),)
    assert answered.spoken == ()


def test_a_refused_movement_is_said_after_the_reply_and_nothing_moves(agent):
    async def scenario(service, stepper):
        decision = await service.decide("turn your arm too far")
        await service.move_arms(decision.directives)
        return decision, stepper.moves

    decision, moves = with_brain(agent, scenario)

    assert decision.directives == () and moves == []
    assert decision.spoken[0] == "PLAIN"
    assert decision.spoken[1] == "I cannot turn an arm more than 360 degrees in one movement."


def test_each_flow_keeps_its_own_session_across_messages(agent):
    async def scenario(service, stepper):
        await service.decide("hello")
        first = [flow.session_id for flow in service.agent_flows]
        await service.decide("hello again")
        return first, [flow.session_id for flow in service.agent_flows]

    first, second = with_brain(agent, scenario)

    assert first == second and all(first) and first[0] != first[1]    # one session per flow, reused


def test_brain_reconnects_every_flow_when_ai_agent_restarts_and_forgets_its_sessions(agent):
    async def scenario(service, stepper):
        await service.decide("hello")
        before = [flow.session_id for flow in service.agent_flows]
        agent.restart()                                    # a real process restart: in-memory sessions are gone
        decision = await service.decide("raise your left arm there and back")
        return before, [flow.session_id for flow in service.agent_flows], decision

    before, after, decision = with_brain(agent, scenario)

    assert all(new not in (None, old) for new, old in zip(after, before))             # a new session in each flow
    assert len(decision.directives) == 2 and decision.spoken == ("PLAIN",)            # and the answer is the real one


def test_brain_follows_the_flows_it_is_configured_with(agent, monkeypatch):
    monkeypatch.setenv("AI_AGENT_FLOWS", "motion-flow")        # a Brain that only decides movements

    async def scenario(service, stepper):
        return [flow.name for flow in service.agent_flows], await service.decide("raise your left arm there and back")

    names, decision = with_brain(agent, scenario)

    assert names == ["motion-flow"]
    assert len(decision.directives) == 2 and decision.spoken == ()
    assert DRAFT not in agent.formats()                        # conversation-flow was never asked

# ------------------------------------------------------------------ the service itself


def test_the_original_session_routes_still_answer_as_conversation_flow(agent):
    base = agent.base_url
    started = httpx.post(f"{base}/session/start", json={"user_id": "tester", "username": "t"}).json()
    session = started["data"]["session_id"]
    reply = httpx.post(f"{base}/session/message", json={"user_id": "tester", "session_id": session, "message": "hello"})
    # the deprecated alias shares conversation-flow's sessions
    again = httpx.post(f"{base}/conversation-flow/session/message",
                       json={"user_id": "tester", "session_id": session, "message": "hello"})

    assert reply.json()["data"]["success"] and again.json()["data"]["success"]
    assert "directive" not in reply.json()["data"] or reply.json()["data"]["directive"] is None
    unknown = httpx.post(f"{base}/motion-flow/session/message",
                         json={"user_id": "tester", "session_id": session, "message": "hello"}).json()
    assert unknown["data"]["error_code"] == "SESSION_NOT_FOUND"      # a conversation session is not a motion session


def test_ai_agent_advertises_the_routes_of_both_flows(agent):
    paths = httpx.get(f"{agent.base_url}/openapi.json", timeout=10).json()["paths"]
    for flow in ("conversation-flow", "motion-flow"):
        for route in ("start", "message", "end"):
            assert f"/{flow}/session/{route}" in paths
