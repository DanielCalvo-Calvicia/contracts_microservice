from contracts.api.common.envelope import ApiEnvelope
from contracts.api.microservices.common.availability import AvailabilityResponse
from contracts.api.microservices.microphone.start import MicrophoneConfig
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
