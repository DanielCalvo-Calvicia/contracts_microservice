"""The whole voice pipeline over real HTTP: Microphone -> Brain -> STT -> Brain -> TTS -> Brain -> Speaker.

Four real microservice processes (each in its own virtualenv, with fake sound card / speech engines,
see ``fake_services.py``) are driven by Brain's real adapters and pipeline. Nothing here inspects a
service's internals: the assertions are on what crossed the wire and what reached the speaker.

Run it with the Brain virtualenv (it needs httpx, pytest and Brain's own packages):

    brain_microservice/windows/Scripts/python.exe -m pytest contracts/tests/e2e -q

It is skipped when a service virtualenv is missing. Set ``RUN_E2E=0`` to skip it explicitly.
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
SERVICES = ("microphone", "stt", "tts", "speaker")


def _venv_python(service: str) -> Path:
    return REPO / f"{service}_microservice" / "windows" / "Scripts" / "python.exe"


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_E2E") == "0" or not all(_venv_python(s).exists() for s in SERVICES),
    reason="needs the four service virtualenvs",
)


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


@pytest.fixture
def stack(tmp_path):
    ports = {name: _free_port() for name in SERVICES}
    sink = tmp_path / "speaker_audio.raw"
    traces = tmp_path / "traces"
    traces.mkdir()
    procs = []
    try:
        for name in SERVICES:
            env = {**os.environ, "E2E_SPEAKER_SINK": str(sink), "E2E_TRACE_DIR": str(traces), "SERVICE_NAME": name}
            procs.append(
                subprocess.Popen(
                    [str(_venv_python(name)), str(FAKE_SERVICES), name, str(ports[name])],
                    cwd=REPO / f"{name}_microservice",
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                )
            )
        deadline = time.monotonic() + 60
        for name in SERVICES:
            while True:
                try:
                    if httpx.get(f"http://127.0.0.1:{ports[name]}/health", timeout=2).status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                assert time.monotonic() < deadline, f"{name} did not start"
                time.sleep(0.2)
        yield ports, sink, traces
    finally:
        for proc in procs:
            proc.terminate()
        for proc in procs:
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()


def test_a_spoken_utterance_travels_the_whole_pipeline_and_arrives_at_the_speaker_at_the_right_rate(stack):
    ports, sink, traces = stack
    brain = REPO / "brain_microservice"
    sys.path.insert(0, str(brain))
    from application.dtos.service_dtos import VoicePipelineServiceRequestDto
    from application.services.service import BrainService
    from infrastructure.outbound.http.base import HttpServiceConfig
    from shared_logging import current_trace_id, span
    from infrastructure.outbound.http.microphone.microphone_adapter import HttpMicrophoneAdapter
    from infrastructure.outbound.http.speaker.speaker_adapter import HttpSpeakerAdapter
    from infrastructure.outbound.http.stt.stt_adapter import HttpSTTAdapter
    from infrastructure.outbound.http.tts.tts_adapter import HttpTTSAdapter
    from tests.shared.fakes import DiagnosticAIAgent, DiagnosticStepper

    def config(name: str, **kwargs) -> HttpServiceConfig:
        return HttpServiceConfig(name, f"http://127.0.0.1:{ports[name]}", timeout_seconds=30, **kwargs)

    async def run():
        with span("e2e voice pipeline"):
            trace_id = current_trace_id()
            return trace_id, await pipeline()

    async def pipeline():
        # Neither ai-agent nor stepper is part of this wire test (it only exercises
        # mic -> STT -> TTS -> speaker, and neither is started as a fake service process here);
        # neither is wired into the live pipeline yet either, so diagnostic fakes stand in.
        # response=None echoes STT's text back unchanged: this test's assertion is about audio
        # format/duration at the given sample rate, not about what ai-agent decided to say.
        service = BrainService(
            HttpMicrophoneAdapter(config("microphone")),
            HttpSTTAdapter(config("stt")),
            HttpTTSAdapter(config("tts")),
            HttpSpeakerAdapter(config("speaker")),
            DiagnosticAIAgent(response=None),
            DiagnosticStepper(),
        )
        return await asyncio.wait_for(
            service.run_voice_pipeline(
                VoicePipelineServiceRequestDto(max_text_segments=1, tts_sample_rate=24000, speaker_channels=1)
            ),
            timeout=60,
        )

    trace_id, result = asyncio.run(run())

    assert result.success, result.message
    assert result.text_segments_forwarded == 1
    # the speaker was told the format Brain asked TTS for ...
    assert sink.with_name(sink.name + ".format").read_text() == "24000,1"
    # ... and TTS really produced it: "hello wire" is 10 characters * 0.1 s at 24 kHz, PCM16 mono
    # (the engine's native 22.05 kHz would give 44100 bytes: the pitch/speed bug this guards against)
    assert abs(len(sink.read_bytes()) - 10 * 2400 * 2) <= 4
    # one trace covers the whole pipeline: every stream carried Brain's trace context, and the code
    # doing the actual work in each service ran inside it (even in background tasks / stream bodies)
    assert trace_id
    for service in SERVICES:
        observed = set((traces / f"{service}.trace").read_text().split())
        assert observed == {trace_id}, f"{service} ran outside Brain's trace: {observed}"
