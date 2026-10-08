"""Brain <-> ai-agent over real HTTP: Brain makes ONE call per utterance and ai-agent identifies the message and
answers it with one flow (conversation, special or movement).

A real ai-agent process (its own virtualenv and REAL composition root: router, flows, routes, sessions, tracing; only
the LLM is replaced by a keyword script, see ``fake_services.build_ai_agent``) is driven by Brain's real
composition root: its real config defaults, real adapters and real ``BrainService.decide``. Only the stepper is
a recorder (its wire is covered by Brain's own tests). The assertions are on what Brain decides to say and move,
and on which phases ai-agent really ran.

Run it with the Brain virtualenv from the workspace root:

    <brain venv python> -m pytest contracts/tests/e2e/test_brain_ai_agent_flows.py -q

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
from venv_paths import venv_python

REPO = Path(__file__).resolve().parents[3]
FAKE_SERVICES = Path(__file__).with_name("fake_services.py")
AI_AGENT_DIR = REPO / "ai-agent"
AI_AGENT_PYTHON = venv_python(AI_AGENT_DIR)

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_E2E") == "0" or not AI_AGENT_PYTHON.exists(),
    reason="needs ai-agent's virtualenv",
)

TRIAGE = "triage_specialist_phase1_response_format"
PLANNER = "motion_planner_phase20_response_format"
PROJECT_MANAGER = "project_manager_phase2_response_format"
DRAFT = "draft_writer_phase7_response_format"
EDITOR = "editor_in_chief_phase8_response_format"
EMOTION = "emotion_reader_phase30_response_format"


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class AIAgentProcess:
    def __init__(self, gestures: bool = False) -> None:
        self.gestures = gestures        # the arm gesture that goes with a reply: off for the tests of the flows themselves
        self.port = _free_port()
        self.base_url = f"http://127.0.0.1:{self.port}"
        self.proc: subprocess.Popen | None = None

    def start(self) -> None:
        self.proc = subprocess.Popen(
            [str(AI_AGENT_PYTHON), str(FAKE_SERVICES), "ai_agent", str(self.port)],
            cwd=AI_AGENT_DIR,
            env={**os.environ, "AI_AGENT_EXPRESSION": "1" if self.gestures else "0", "AI_AGENT_EXPRESSION_SEED": "3"},
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


@pytest.fixture(scope="module")
def expressive_agent():
    process = AIAgentProcess(gestures=True)
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
# Brain makes one call per utterance. ai-agent identifies the message (triage) and the domain picks the flow:
# communication -> conversation, movement -> movement, anything else -> special.


def test_a_plain_message_is_answered_by_the_conversation_flow_and_moves_nothing(agent):
    async def scenario(service, stepper):
        return await service.decide("hello there")

    decision = with_brain(agent, scenario)

    assert decision.spoken == ("PLAIN",)
    assert decision.directives == () and decision.failed_flows == () and decision.awaiting_user_input is False
    assert agent.formats() == [TRIAGE, DRAFT, EDITOR]       # identified, written, polished: nothing planned or moved


def test_a_task_is_answered_by_the_special_flow_after_planning(agent):
    async def scenario(service, stepper):
        return await service.decide("make a table of my family")

    decision = with_brain(agent, scenario)

    assert decision.spoken == ("PLANNED",) and decision.directives == ()
    formats = agent.formats()
    assert formats[0] == TRIAGE and PROJECT_MANAGER in formats and formats[-2:] == [DRAFT, EDITOR]
    assert PLANNER not in formats


def test_a_movement_sequence_is_understood_ordered_announced_and_run(agent):
    async def scenario(service, stepper):
        decision = await service.decide("raise your left arm there and back")
        await service.move_arms(decision.directives)
        return decision, stepper.moves

    decision, moves = with_brain(agent, scenario)

    expected = (directive("left", 90.0, "forward"), directive("left", -90.0, "forward"))
    assert decision.directives == expected                # the list, in order, signed degrees intact
    assert tuple(moves) == expected                       # and Brain would send them to the stepper in that order
    assert decision.spoken == ("Moving my left arm.",)    # the movement flow announces what it is about to do
    assert agent.formats() == [TRIAGE, PLANNER]           # no writer, no plan: only the movement flow ran


def test_a_movement_is_silent_when_brain_is_told_not_to_speak_it(agent, monkeypatch):
    monkeypatch.setenv("AI_AGENT_SPEAK_MOVEMENTS", "0")

    async def scenario(service, stepper):
        return await service.decide("raise your left arm there and back")

    decision = with_brain(agent, scenario)

    assert len(decision.directives) == 2 and decision.spoken == ()    # moves, says nothing


def test_a_missing_detail_is_asked_and_the_answer_goes_straight_to_the_movement_flow(agent):
    async def scenario(service, stepper):
        asked = await service.decide("move my arm")
        before_the_answer = len(agent.formats())
        answered = await service.decide("thirty degrees, 30 degrees")
        return asked, agent.formats()[before_the_answer:], answered

    asked, calls_for_the_answer, answered = with_brain(agent, scenario)

    assert asked.spoken == ("Which arm, and how many degrees?",) and asked.directives == ()
    assert asked.awaiting_user_input is True              # Brain speaks the question and does not move
    assert TRIAGE not in calls_for_the_answer and DRAFT not in calls_for_the_answer   # not identified again
    assert PLANNER in calls_for_the_answer                # ai-agent resumed the movement flow that asked
    assert answered.directives == (directive("left", 30.0, "forward"),)
    assert answered.awaiting_user_input is False


def test_a_refused_movement_is_said_and_nothing_moves(agent, monkeypatch):
    monkeypatch.setenv("AI_AGENT_SPEAK_MOVEMENTS", "0")    # a refusal is said even when movements are silent

    async def scenario(service, stepper):
        decision = await service.decide("turn your arm too far")
        await service.move_arms(decision.directives)
        return decision, stepper.moves

    decision, moves = with_brain(agent, scenario)

    assert decision.directives == () and moves == []
    assert decision.spoken == ("I cannot turn an arm more than 360 degrees in one movement.",)


def test_brain_keeps_one_session_with_ai_agent_across_messages(agent):
    async def scenario(service, stepper):
        await service.decide("hello")
        first = [flow.session_id for flow in service.agent_flows]
        await service.decide("hello again")
        return [flow.name for flow in service.agent_flows], first, [flow.session_id for flow in service.agent_flows]

    names, first, second = with_brain(agent, scenario)

    assert names == ["ai-agent"]
    assert first == second and all(first)                 # one session, reused


def test_brain_reconnects_when_ai_agent_restarts_and_forgets_its_session(agent):
    async def scenario(service, stepper):
        await service.decide("hello")
        before = [flow.session_id for flow in service.agent_flows]
        agent.restart()                                    # a real process restart: in-memory sessions are gone
        decision = await service.decide("raise your left arm there and back")
        return before, [flow.session_id for flow in service.agent_flows], decision

    before, after, decision = with_brain(agent, scenario)

    assert all(new not in (None, old) for new, old in zip(after, before))             # a new session
    assert len(decision.directives) == 2 and decision.spoken == ("Moving my left arm.",)   # and the answer is the real one


# ------------------------------------------------------------------ the service itself


def test_the_session_routes_say_which_flow_answered(agent):
    base = agent.base_url
    session = httpx.post(f"{base}/session/start", json={"user_id": "tester", "username": "t"}).json()["data"]["session_id"]

    def say(text):
        return httpx.post(f"{base}/session/message", json={"user_id": "tester", "session_id": session, "message": text},
                          timeout=30).json()["data"]

    assert say("hello")["flow"] == "conversation"
    assert say("make a table of my family")["flow"] == "special"
    moved = say("raise your left arm there and back")
    assert moved["flow"] == "movement" and len(moved["directives"]) == 2
    silent = httpx.post(f"{base}/session/message", json={
        "user_id": "tester", "session_id": session, "message": "raise your left arm there and back",
        "speak_movements": False}, timeout=30).json()["data"]
    assert silent["response"] == "" and len(silent["directives"]) == 2


def test_ai_agent_has_one_set_of_session_routes_and_no_routes_per_flow(agent):
    paths = httpx.get(f"{agent.base_url}/openapi.json", timeout=10).json()["paths"]
    for route in ("start", "message", "end"):
        assert f"/session/{route}" in paths
    assert not [path for path in paths if "conversation-flow" in path or "motion-flow" in path]


# ------------------------------------------------------------------ the gesture that goes with a reply


def test_a_reply_comes_with_a_gesture_for_its_emotion_and_a_movement_asked_for_does_not(expressive_agent):
    # Brain's own adapter against the real ai-agent process: the gesture arrives with its pauses and its flag
    brain_dir = str(REPO / "brain_microservice")
    if brain_dir not in sys.path:
        sys.path.insert(0, brain_dir)
    os.environ["AI_AGENT_BASE_URL"] = expressive_agent.base_url
    from application.dtos.outbound_dtos import AgentFlowRequestDto, AIAgentStartSessionRequestDto
    from composition_root.config import load_config
    from composition_root.dependencies.brain_dependency import generate_brain_core_dependency

    expressive_agent.reset()

    async def main():
        core = generate_brain_core_dependency(load_config())
        adapter = core.agent_flow_adapters[0]
        try:
            session = await adapter.start_session(AIAgentStartSessionRequestDto(username="e2e"))
            happy = await adapter.message(AgentFlowRequestDto(session_id=session.session_id, message="I just got a puppy!"))
            asked = await adapter.message(AgentFlowRequestDto(session_id=session.session_id, message="turn your left arm 90 degrees"))
            return happy, asked
        finally:
            for closing in (core.microphone_adapter, core.stt_adapter, core.tts_adapter, core.speaker_adapter,
                            *core.agent_flow_adapters, core.stepper_adapter):
                await closing.close()

    happy, asked = asyncio.run(main())

    assert happy.flow == "conversation" and happy.spoken == "PLAIN"
    assert happy.gesture is True and happy.directives
    assert happy.directives[0].pause_seconds == 0.0                      # starts with the speech
    assert all(d.pause_seconds >= 0 and d.arm in ("left", "right") for d in happy.directives)
    assert EMOTION in expressive_agent.formats()
    assert asked.flow == "movement" and asked.gesture is False           # the user asked: the robot does just that


def test_brain_decides_a_gesture_for_a_reply_and_plain_movements_for_a_request(expressive_agent):
    async def scenario(service, stepper):
        happy = await service.decide("I just got a puppy!")
        asked = await service.decide("turn your left arm 90 degrees")
        return happy, asked

    happy, asked = with_brain(expressive_agent, scenario)

    assert happy.spoken == ("PLAIN",) and happy.gesture is True and happy.directives
    assert happy.directives[0].pause_seconds == 0.0                       # starts with the speech
    assert asked.gesture is False and [d.degrees for d in asked.directives] == [90.0]
