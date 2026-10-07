"""The flows of ai-agent stay separate: a message is identified once and then answered by exactly ONE flow.

A real ai-agent process (real composition root; only the LLM is a keyword script, see ``fake_services.build_ai_agent``)
is called over HTTP like any client would: start a session, send a sentence, read ``data.flow`` and look at which
phases ran (the LLM calls the service made). The sentences are ordinary things a user says; none of them names a
flow, a phase or a tool. Each flow is proved by what it did AND by what it did not do.

    <brain venv python> -m pytest contracts/tests/e2e/test_flow_separation.py -q
"""

import os

import httpx
import pytest
from test_brain_ai_agent_flows import AI_AGENT_PYTHON, AIAgentProcess

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_E2E") == "0" or not AI_AGENT_PYTHON.exists(),
    reason="needs ai-agent's virtualenv",
)

TRIAGE = "triage_specialist_phase1_response_format"
PLANNER = "motion_planner_phase20_response_format"
PROJECT_MANAGER = "project_manager_phase2_response_format"
GATE = "safety_quality_gatekeeper_phase3_response_format"
DRAFT = "draft_writer_phase7_response_format"
EDITOR = "editor_in_chief_phase8_response_format"

# What only one flow runs. Everything else must stay out of the other flows.
ONLY_SPECIAL = {PROJECT_MANAGER, GATE}
ONLY_MOVEMENT = {PLANNER}
WRITING = {DRAFT, EDITOR}

CONVERSATION_SENTENCES = [
    "Hello there!",
    "How are you today?",
    "Thank you, that was helpful.",
    "What is your name?",
]
MOVEMENT_SENTENCES = [
    "Please raise your left arm.",
    "Turn your right arm a quarter turn.",
    "Move your left arm forward and then bring it back.",
]
SPECIAL_SENTENCES = [
    "Make me a table with the members of my family.",
    "Write a short report about my week.",
    "Plan my day for tomorrow.",
]


@pytest.fixture(scope="module")
def agent():
    process = AIAgentProcess()
    process.start()
    try:
        yield process
    finally:
        process.stop()


def say(agent: AIAgentProcess, sentence: str) -> tuple[dict, list[str]]:
    """One sentence in a fresh session: ai-agent's answer and the phases (LLM calls) it ran for it."""
    base = agent.base_url
    session = httpx.post(f"{base}/session/start", json={"user_id": "tester", "username": "t"}).json()["data"]["session_id"]
    agent.reset()
    answer = httpx.post(f"{base}/session/message", timeout=30,
                        json={"user_id": "tester", "session_id": session, "message": sentence}).json()["data"]
    return answer, agent.formats()


def phases_of(formats: list[str]) -> set[str]:
    """The phases that ran, with the per-action ones (workers, MCP operator) folded into one name."""
    return {"single_action" if "single_action" in fmt else fmt for fmt in formats}


@pytest.mark.parametrize("sentence", CONVERSATION_SENTENCES)
def test_ordinary_talk_is_answered_by_the_conversation_flow_alone(agent, sentence):
    answer, formats = say(agent, sentence)

    assert answer["success"] and answer["flow"] == "conversation"
    assert answer["response"].strip() and answer["directives"] == []
    assert formats[0] == TRIAGE and formats.count(TRIAGE) == 1          # identified once, first
    assert WRITING <= phases_of(formats)                                  # it wrote and polished a reply
    assert not phases_of(formats) & (ONLY_SPECIAL | ONLY_MOVEMENT)        # no planning, no checking, no movement
    assert "single_action" not in phases_of(formats)                      # no actions were executed


@pytest.mark.parametrize("sentence", MOVEMENT_SENTENCES)
def test_a_request_to_move_is_answered_by_the_movement_flow_alone(agent, sentence):
    answer, formats = say(agent, sentence)

    assert answer["success"] and answer["flow"] == "movement"
    assert answer["directives"], "a movement was asked, so movements must come back"
    assert all(d["arm"] in ("left", "right") for d in answer["directives"])
    assert formats[0] == TRIAGE and formats.count(TRIAGE) == 1
    assert ONLY_MOVEMENT <= phases_of(formats)
    assert not phases_of(formats) & (WRITING | ONLY_SPECIAL)              # no writer, no editor, no plan
    assert "single_action" not in phases_of(formats)


@pytest.mark.parametrize("sentence", SPECIAL_SENTENCES)
def test_a_task_is_answered_by_the_special_flow_alone(agent, sentence):
    answer, formats = say(agent, sentence)

    assert answer["success"] and answer["flow"] == "special"
    assert answer["response"].strip() and answer["directives"] == []
    assert formats[0] == TRIAGE and formats.count(TRIAGE) == 1
    assert ONLY_SPECIAL <= phases_of(formats)                             # planned and checked ...
    assert "single_action" in phases_of(formats)                          # ... executed ...
    assert WRITING <= phases_of(formats)                                  # ... and written
    assert PLANNER not in formats                                         # never touched the movement flow


def test_every_message_is_identified_before_anything_answers(agent):
    for sentence in (CONVERSATION_SENTENCES[0], MOVEMENT_SENTENCES[0], SPECIAL_SENTENCES[0]):
        _, formats = say(agent, sentence)
        assert formats[0] == TRIAGE


def test_the_three_kinds_of_message_never_end_up_in_the_same_flow(agent):
    flows = {say(agent, sentence)[0]["flow"]
             for sentence in (CONVERSATION_SENTENCES[0], MOVEMENT_SENTENCES[0], SPECIAL_SENTENCES[0])}
    assert flows == {"conversation", "movement", "special"}


def test_only_the_movement_flow_ever_returns_movements(agent):
    for sentence in CONVERSATION_SENTENCES + SPECIAL_SENTENCES:
        assert say(agent, sentence)[0]["directives"] == []


def test_the_flows_do_not_leak_into_each_other_inside_one_session(agent):
    """One conversation that goes talk -> task -> movement -> talk: each turn is answered by its own flow."""
    base = agent.base_url
    session = httpx.post(f"{base}/session/start", json={"user_id": "tester", "username": "t"}).json()["data"]["session_id"]
    seen = []
    for sentence in (CONVERSATION_SENTENCES[0], SPECIAL_SENTENCES[0], MOVEMENT_SENTENCES[0], CONVERSATION_SENTENCES[1]):
        data = httpx.post(f"{base}/session/message", timeout=30,
                          json={"user_id": "tester", "session_id": session, "message": sentence}).json()["data"]
        seen.append((data["flow"], bool(data["directives"])))

    assert seen == [("conversation", False), ("special", False), ("movement", True), ("conversation", False)]


def test_a_movement_can_be_made_silent_without_changing_which_flow_answers(agent):
    base = agent.base_url
    session = httpx.post(f"{base}/session/start", json={"user_id": "tester", "username": "t"}).json()["data"]["session_id"]
    data = httpx.post(f"{base}/session/message", timeout=30, json={
        "user_id": "tester", "session_id": session, "message": MOVEMENT_SENTENCES[0],
        "speak_movements": False}).json()["data"]

    assert data["flow"] == "movement" and data["directives"] and data["response"] == ""
