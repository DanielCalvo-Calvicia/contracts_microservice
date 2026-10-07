from contracts.api.common.envelope import ApiEnvelope
from contracts.api.microservices.ai_agent.decision import MotorDirective
from contracts.api.microservices.ai_agent.session import (
    AIAgentEndSessionResponse,
    AIAgentMessageRequest,
    AIAgentMessageResponse,
    AIAgentStartSessionResponse,
)
from contracts.api.microservices.common.availability import AvailabilityResponse
from contracts.api.microservices.microphone.start import MicrophoneConfig
from contracts.api.microservices.stepper.batch import StepperBatchResult
from contracts.api.microservices.tts.process_batch import ProcessBatchResponse


def test_success_serializes_the_contract_dataclass_as_data():
    body = ApiEnvelope.success("check_availability", "ok", AvailabilityResponse(is_available=True)).to_dict()

    assert set(body) == {"action", "status", "status_code", "message", "timestamp", "data"}
    assert (body["status"], body["status_code"]) == ("success", 200)
    assert body["data"] == {"is_available": True, "reason": None}


def test_accepted_and_failure_shapes():
    accepted = ApiEnvelope.accepted("set_stream", "queued").to_dict()
    failure = ApiEnvelope.failure("process_batch", "boom", 400, "No text").to_dict()

    assert (accepted["status"], accepted["status_code"], accepted["data"]) == ("accepted", 202, None)
    assert (failure["status"], failure["status_code"], failure["data"]) == ("error", 400, "No text")


def test_endpoint_data_shapes_match_what_the_services_send():
    assert ApiEnvelope.success("start_stream", "ok", MicrophoneConfig(sample_rate=8000)).to_dict()["data"] == {
        "sample_rate": 8000,
        "channels": 1,
        "encoding": "pcm16",
        "frame_ms": 20,
        "chunk_size": 1024,
        "device_id": None,
    }
    batch = ProcessBatchResponse(audio_data_base64="AA==", sample_rate=24000, channels=1)
    assert ApiEnvelope.success("process_batch", "ok", batch).to_dict()["data"] == {
        "audio_data_base64": "AA==",
        "sample_rate": 24000,
        "channels": 1,
    }


def test_ai_agent_session_data_shapes_match_what_the_service_sends():
    start = AIAgentStartSessionResponse(success=True, session_id="s1", message="Session started successfully.")
    assert ApiEnvelope.success("start_session", "ok", start).to_dict()["data"] == {
        "success": True, "session_id": "s1", "message": "Session started successfully.", "error_code": None,
    }

    not_found = AIAgentEndSessionResponse(success=False, message="Session ID not found.", error_code="SESSION_NOT_FOUND")
    assert ApiEnvelope.success("end_session", "ok", not_found).to_dict()["data"] == {
        "success": False, "message": "Session ID not found.", "error_code": "SESSION_NOT_FOUND",
    }


def test_ai_agent_message_response_serializes_an_ordered_list_of_nested_motor_directives():
    """dataclasses.asdict (what ApiEnvelope.to_dict uses) must recurse into MotorDirective too,
    not leave it as a dataclass instance in the JSON-bound dict."""
    reply = AIAgentMessageResponse(
        success=True, response="Moving my left arm there and back.", flow="movement",
        directives=(
            MotorDirective(arm="left", degrees=90.0, direction="forward"),
            MotorDirective(arm="left", degrees=-90.0, direction="forward"),
        ),
    )
    assert ApiEnvelope.success("message_received", "ok", reply).to_dict()["data"] == {
        "success": True, "response": "Moving my left arm there and back.",
        "message": None, "error_code": None,
        "directives": (
            {"arm": "left", "degrees": 90.0, "direction": "forward"},
            {"arm": "left", "degrees": -90.0, "direction": "forward"},
        ),
        "awaiting_user_input": False, "flow": "movement",
    }


def test_ai_agent_message_response_without_movement_has_no_directives_and_no_flow():
    reply = AIAgentMessageResponse(success=True, response="Hi there!")
    data = ApiEnvelope.success("message_received", "ok", reply).to_dict()["data"]
    assert data["directives"] == () and data["awaiting_user_input"] is False and data["flow"] is None


def test_ai_agent_message_response_can_carry_a_question_for_the_user():
    reply = AIAgentMessageResponse(success=True, response="How many degrees?", awaiting_user_input=True,
                                   flow="movement")
    data = ApiEnvelope.success("message_received", "ok", reply).to_dict()["data"]
    assert data["awaiting_user_input"] is True and data["directives"] == ()


def test_ai_agent_message_request_defaults_to_speaking_movements():
    assert AIAgentMessageRequest(session_id="s", message="hi").speak_movements is True
    assert AIAgentMessageRequest(session_id="s", message="hi", speak_movements=False).speak_movements is False


def test_the_deprecated_two_route_contracts_are_gone():
    import importlib
    import pytest

    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("contracts.api.microservices.ai_agent.motion")
    decision = importlib.import_module("contracts.api.microservices.ai_agent.decision")
    assert not hasattr(decision, "RobotContext")
    assert not hasattr(AIAgentMessageRequest(session_id="s", message="hi"), "robot_context")
    assert not hasattr(AIAgentMessageResponse(success=True), "directive")


def test_the_flow_names_are_the_four_flows_of_ai_agent():
    from typing import get_args

    from contracts.api.microservices.ai_agent.decision import AgentFlowName

    assert get_args(AgentFlowName) == ("identification", "conversation", "special", "movement")


def test_stepper_batch_result_data_shape_matches_what_the_service_sends():
    result = StepperBatchResult(success=True, message="Successfully completed 200 steps.")
    assert ApiEnvelope.success("rotate", "ok", result).to_dict()["data"] == {
        "success": True, "message": "Successfully completed 200 steps.",
    }
