"""The whole OBLIVION pipeline with REAL services and mocked INPUT DATA only.

    speech WAV -> real microphone service -> real STT (whisper) -> Brain -> real ai-agent (real LLM)
               -> Brain -> real TTS (SAPI) -> real speaker (plays out loud)
                       \\-> real stepper service (its own mock-hardware mode) on a movement decision

Every service runs exactly as in production (its own main.py / composition root and engine). The only
substitution is the microphone's capture device: a phrase synthesized with the real SAPI voice is
streamed in real time, as if somebody said it (see ``real_services.py``). Brain runs in this process
with its real adapters; "taps" around them only RECORD what crosses each boundary.

It costs real LLM calls and plays audio on this machine, so it only runs when asked:

    set E2E_REAL_LLM=1 and export the provider keys of ai-agent/config/step_models.json
    (e.g. GROQ_API_KEY/GROQ_URL, GOOGLE_API_KEY/GOOGLE_URL; never put them in a file this test reads)
    brain_microservice/windows/Scripts/python.exe -m pytest contracts/tests/e2e/test_real_pipeline.py -q

A real LLM is not deterministic: the movement assertions check the directive's fields, which is what
the prompts ask for, so an occasional failure there is a finding about the prompt or the model.
"""

import asyncio
import dataclasses
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

REPO = Path(__file__).resolve().parents[3]
LAUNCHER = Path(__file__).with_name("real_services.py")
MAKE_SPEECH = Path(__file__).with_name("make_speech.py")
FOLDERS = {
    "microphone": "microphone_microservice",
    "stt": "stt_microservice",
    "tts": "tts_microservice",
    "speaker": "speaker_microservice",
    "ai_agent": "ai-agent",
    "stepper": "stepper_microservice",
}
ALL_SERVICES = tuple(FOLDERS)


def _venv_python(service: str) -> Path:
    return REPO / FOLDERS[service] / "windows" / "Scripts" / "python.exe"


pytestmark = pytest.mark.skipif(
    os.environ.get("E2E_REAL_LLM") != "1" or not all(_venv_python(s).exists() for s in ALL_SERVICES),
    reason="real services + real LLM: set E2E_REAL_LLM=1 (and the provider keys) to run",
)

LOOP = asyncio.new_event_loop()  # Brain's httpx clients are bound to the loop they first run in


def run(coro):
    return LOOP.run_until_complete(coro)


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _wait_healthy(port: int, name: str, log: Path) -> None:
    deadline = time.monotonic() + 240  # whisper loads its model before the service answers
    while True:
        try:
            if httpx.get(f"http://127.0.0.1:{port}/health", timeout=2).status_code == 200:
                return
        except httpx.HTTPError:
            pass
        assert time.monotonic() < deadline, f"{name} did not start; see {log}"
        time.sleep(0.5)


class Stack:
    """Real service processes. A port is reserved for every service even if it is not started, so a
    service that is "down" is a genuine connection refused."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.ports = {name: _free_port() for name in ALL_SERVICES}
        self.current_wav = root / "current_speech.wav"
        self._procs: dict[str, subprocess.Popen] = {}
        (root / "logs").mkdir(parents=True, exist_ok=True)

    def start(self, services=ALL_SERVICES) -> "Stack":
        for name in services:
            self._launch(name)
        for name in services:
            _wait_healthy(self.ports[name], name, self.log(name))
        return self

    def log(self, name: str) -> Path:
        return self.root / "logs" / f"{name}.log"

    def _env(self, name: str) -> dict[str, str]:
        port = str(self.ports[name])
        env = {
            **os.environ,
            "PYTHONUNBUFFERED": "1",
            "SERVICE_HOST": "127.0.0.1",
            "SERVICE_PORT": port,
            "E2E_MIC_WAV": str(self.current_wav),
            "STT_ENGINE": "local",  # the real whisper model, on CPU
            "STT_LANGUAGE": "en",
            "MOCK_HARDWARE": "1",  # stepper's own mock driver: there is no GPIO on this machine
            "STEPPER_CONFIGS": '{"stepper_1": {"step": 17, "dir": 27, "en": 5}, "stepper_2": {"step": 22, "dir": 23, "en": 6}}',
            "STEPS_PER_REVOLUTION": "200",
            "AI_AGENT_HOST": "127.0.0.1",
            "AI_AGENT_PORT": port,
            "AI_AGENT_RELOAD": "0",
        }
        return env

    def _launch(self, name: str) -> None:
        with open(self.log(name), "ab") as log:
            self._procs[name] = subprocess.Popen(
                [str(_venv_python(name)), str(LAUNCHER), name],
                cwd=REPO / FOLDERS[name],
                env=self._env(name),
                stdout=log,
                stderr=subprocess.STDOUT,
            )

    def restart(self, name: str) -> None:
        """Same port, fresh process: it forgets everything it kept in memory."""
        self._stop_one(self._procs.pop(name))
        self._launch(name)
        _wait_healthy(self.ports[name], name, self.log(name))

    def say(self, wav: Path) -> None:
        shutil.copyfile(wav, self.current_wav)

    @staticmethod
    def _stop_one(proc: subprocess.Popen) -> None:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()

    def stop(self) -> None:
        for proc in self._procs.values():
            self._stop_one(proc)


@pytest.fixture(scope="module")
def speech(tmp_path_factory):
    """phrase -> WAV synthesized by the real SAPI voice (the mocked input data), cached."""
    directory = tmp_path_factory.mktemp("speech")
    cache: dict[str, Path] = {}

    def synthesize(phrase: str) -> Path:
        if phrase not in cache:
            out = directory / f"phrase_{len(cache)}.wav"
            subprocess.run([str(_venv_python("tts")), str(MAKE_SPEECH), phrase, str(out)], check=True, timeout=120)
            cache[phrase] = out
        return cache[phrase]

    return synthesize


@pytest.fixture(scope="module")
def live(tmp_path_factory, speech):
    """One full stack for the scenarios that do not break anything (whisper loads once)."""
    stack = Stack(tmp_path_factory.mktemp("live"))
    stack.say(speech("Hello."))
    try:
        yield stack.start()
    finally:
        stack.stop()


@pytest.fixture
def fresh(tmp_path, speech):
    """A private stack, for scenarios that restart or omit a service."""
    stacks: list[Stack] = []

    def make(services=ALL_SERVICES) -> Stack:
        stack = Stack(tmp_path)
        stack.say(speech("Hello."))
        stacks.append(stack)
        return stack.start(services)

    yield make
    for stack in stacks:
        stack.stop()


# ------------------------------------------------------------------ Brain (real) + recording taps


class Tap:
    """Forwards everything to the real adapter; subclasses only record what passes through."""

    def __init__(self, inner) -> None:
        self._inner = inner

    def __getattr__(self, name):
        return getattr(self._inner, name)


class AIAgentTap(Tap):
    def __init__(self, inner) -> None:
        super().__init__(inner)
        self.transcripts: list[str] = []  # what real STT heard: the text sent to ai-agent
        self.replies = []  # what the real LLM decided

    async def message(self, request):
        self.transcripts.append(request.message)
        reply = await self._inner.message(request)
        self.replies.append(reply)
        return reply


class StepperTap(Tap):
    def __init__(self, inner) -> None:
        super().__init__(inner)
        self.results = []
        self.errors: list[BaseException] = []

    async def move(self, directive):
        try:
            result = await self._inner.move(directive)
        except BaseException as error:
            self.errors.append(error)
            raise
        self.results.append(result)
        return result


class TTSTap(Tap):
    def __init__(self, inner) -> None:
        super().__init__(inner)
        self.spoken: list[str] = []  # the texts real TTS was asked to say

    async def set_text_stream(self, request):
        from contracts.stream.codec import NdjsonDecoder
        from contracts.stream.common.base import EventType
        from contracts.stream.schemas import TTS_INBOUND

        decoder = NdjsonDecoder(TTS_INBOUND)
        source = request.text_stream

        async def tapped():
            async for chunk in source:
                for event in decoder.feed(chunk):
                    if event.type is EventType.COMPLETED and event.payload.output:
                        self.spoken.append(event.payload.output)
                yield chunk

        await self._inner.set_text_stream(dataclasses.replace(request, text_stream=tapped()))


class SpeakerTap(Tap):
    def __init__(self, inner) -> None:
        super().__init__(inner)
        self.pcm_bytes = 0  # audio bytes the real speaker was handed
        self.responses = []

    async def play_stream(self, request):
        import base64

        from contracts.stream.codec import NdjsonDecoder
        from contracts.stream.common.base import EventType
        from contracts.stream.schemas import SPEAKER_INBOUND

        decoder = NdjsonDecoder(SPEAKER_INBOUND)
        source = request.audio_stream

        async def tapped():
            async for chunk in source:
                for event in decoder.feed(chunk):
                    if event.type is EventType.PARTIAL:
                        self.pcm_bytes += len(base64.b64decode(event.payload.bytes_base64))
                yield chunk

        response = await self._inner.play_stream(dataclasses.replace(request, audio_stream=tapped()))
        self.responses.append(response)
        return response


@dataclasses.dataclass
class Brain:
    service: object
    ai_agent: AIAgentTap
    stepper: StepperTap
    tts: TTSTap
    speaker: SpeakerTap
    adapters: list

    async def close(self) -> None:
        for adapter in self.adapters:
            await adapter.close()


def make_brain(ports: dict[str, int]) -> Brain:
    brain_dir = str(REPO / "brain_microservice")
    if brain_dir not in sys.path:
        sys.path.insert(0, brain_dir)
    from application.services.service import BrainService
    from infrastructure.outbound.http.ai_agent.ai_agent_adapter import HttpAIAgentAdapter
    from infrastructure.outbound.http.base import HttpServiceConfig
    from infrastructure.outbound.http.microphone.microphone_adapter import HttpMicrophoneAdapter
    from infrastructure.outbound.http.speaker.speaker_adapter import HttpSpeakerAdapter
    from infrastructure.outbound.http.stepper.stepper_adapter import HttpStepperAdapter
    from infrastructure.outbound.http.stt.stt_adapter import HttpSTTAdapter
    from infrastructure.outbound.http.tts.tts_adapter import HttpTTSAdapter

    def config(name: str) -> HttpServiceConfig:
        return HttpServiceConfig(name, f"http://127.0.0.1:{ports[name]}", timeout_seconds=120)

    real = {
        "microphone": HttpMicrophoneAdapter(config("microphone")),
        "stt": HttpSTTAdapter(config("stt")),
        "tts": HttpTTSAdapter(config("tts")),
        "speaker": HttpSpeakerAdapter(config("speaker")),
        "ai_agent": HttpAIAgentAdapter(config("ai_agent")),
        "stepper": HttpStepperAdapter(
            config("stepper"), left_arm_stepper_id="stepper_1", right_arm_stepper_id="stepper_2", default_rpm=15.0
        ),
    }
    tts, speaker = TTSTap(real["tts"]), SpeakerTap(real["speaker"])
    ai_agent, stepper = AIAgentTap(real["ai_agent"]), StepperTap(real["stepper"])
    service = BrainService(real["microphone"], real["stt"], tts, speaker, ai_agent, stepper)
    return Brain(service, ai_agent, stepper, tts, speaker, list(real.values()))


async def say_and_run(stack: Stack, brain: Brain, wav: Path, *, wait_for_move: bool = False):
    """Someone 'says' the phrase; one pipeline run (one decision), then the microphone is released."""
    from application.dtos.service_dtos import VoicePipelineServiceRequestDto

    stack.say(wav)
    try:
        result = await asyncio.wait_for(
            brain.service.run_voice_pipeline(
                VoicePipelineServiceRequestDto(max_text_segments=1, tts_sample_rate=24000, speaker_channels=1)
            ),
            timeout=180,
        )
    finally:
        await brain.service.microphone_port.stop_stream()
    if wait_for_move:  # the movement is a fire-and-forget task that outlives the run
        deadline = time.monotonic() + 30
        while not (brain.stepper.results or brain.stepper.errors) and time.monotonic() < deadline:
            await asyncio.sleep(0.1)
    return result


def scenario(stack: Stack, speech, phrase: str, *, wait_for_move: bool = False, brain: Brain | None = None):
    brain = brain or make_brain(stack.ports)
    try:
        result = run(say_and_run(stack, brain, speech(phrase), wait_for_move=wait_for_move))
    finally:
        pass
    return brain, result


def _heard(brain: Brain) -> str:
    return " ".join(brain.ai_agent.transcripts).lower()


# ------------------------------------------------------------------ scenarios


def test_a_greeting_is_understood_answered_and_spoken_without_moving_anything(live, speech):
    brain, result = scenario(live, speech, "Hello, how are you today?")

    assert result.success, result.message
    assert "hello" in _heard(brain)  # real whisper understood the synthesized speech
    (reply,) = brain.ai_agent.replies  # real LLM
    assert reply.success and reply.response.strip() and reply.directive is None
    assert brain.tts.spoken == [reply.response.strip()]  # what real TTS was told to say
    assert brain.speaker.pcm_bytes > 24000  # real audio reached the real speaker (>0.5 s at 24 kHz)
    assert brain.speaker.responses[0].success
    assert not brain.stepper.results and not brain.stepper.errors
    run(brain.close())


def test_a_movement_request_moves_the_left_arm_on_the_real_stepper_service(live, speech):
    brain, result = scenario(live, speech, "Please rotate your left arm ninety degrees forward.", wait_for_move=True)

    assert result.success, result.message
    assert "left" in _heard(brain)
    (reply,) = brain.ai_agent.replies
    assert reply.directive is not None, f"the LLM planned no movement: {reply.response!r}"
    assert (reply.directive.arm, reply.directive.degrees, reply.directive.direction) == ("left", 90.0, "forward")
    assert brain.tts.spoken == [reply.response.strip()]
    assert brain.speaker.pcm_bytes > 24000
    (move,) = brain.stepper.results  # answered by the real stepper service (0.25 rev * 200 = 50 steps)
    assert move.success and "50 steps" in move.message, move
    run(brain.close())


def test_a_backwards_request_for_the_right_arm_reaches_the_other_stepper(live, speech):
    brain, result = scenario(live, speech, "Turn your right arm forty five degrees backwards.", wait_for_move=True)

    assert result.success, result.message
    (reply,) = brain.ai_agent.replies
    assert reply.directive is not None, f"the LLM planned no movement: {reply.response!r}"
    assert (reply.directive.arm, reply.directive.degrees, reply.directive.direction) == ("right", 45.0, "reverse")
    (move,) = brain.stepper.results  # 45 degrees = 0.125 rev * 200 = 25 steps
    assert move.success and "25 steps" in move.message, move
    run(brain.close())


def test_something_the_robot_cannot_do_is_refused_out_loud_and_nothing_moves(live, speech):
    brain, result = scenario(live, speech, "Please delete all the files on my computer.")

    assert result.success, result.message
    (reply,) = brain.ai_agent.replies
    assert reply.success and reply.response.strip() and reply.directive is None
    assert brain.tts.spoken == [reply.response.strip()]
    assert brain.speaker.pcm_bytes > 24000
    assert not brain.stepper.results and not brain.stepper.errors
    run(brain.close())


def test_a_second_conversation_reuses_the_same_ai_agent_session(live, speech):
    brain = make_brain(live.ports)
    _, first = scenario(live, speech, "Hello.", brain=brain)
    session = brain.service._ai_agent_session_id
    _, second = scenario(live, speech, "Good morning.", brain=brain)

    assert first.success and second.success
    assert session and brain.service._ai_agent_session_id == session
    assert len(brain.ai_agent.replies) == 2 and all(r.success for r in brain.ai_agent.replies)
    run(brain.close())


def test_every_real_service_reports_healthy_and_available(live):
    brain = make_brain(live.ports)

    async def check_all():
        return {name: (await adapter.check_health()).is_available for name, adapter in zip(ALL_SERVICES, brain.adapters)}

    assert run(check_all()) == {name: True for name in ALL_SERVICES}
    run(brain.close())


def test_brain_reconnects_when_the_real_ai_agent_restarts_and_forgets_its_session(fresh, speech):
    stack = fresh()
    brain = make_brain(stack.ports)
    _, first = scenario(stack, speech, "Hello.", brain=brain)
    session = brain.service._ai_agent_session_id
    assert first.success and session

    stack.restart("ai_agent")  # a real process restart: its in-memory sessions are gone
    _, second = scenario(stack, speech, "Good morning.", brain=brain)

    assert second.success, second.message
    codes = [r.error_code for r in brain.ai_agent.replies]
    assert "SESSION_NOT_FOUND" in codes  # the stale session was refused...
    assert brain.ai_agent.replies[-1].success  # ...and Brain opened a new one and got a real answer
    assert brain.service._ai_agent_session_id not in (None, session)
    run(brain.close())


def test_a_real_ai_agent_that_is_down_is_answered_with_the_fallback_apology(fresh, speech):
    stack = fresh([s for s in ALL_SERVICES if s != "ai_agent"])
    brain, result = scenario(stack, speech, "Hello.")

    from application.services.steps.stream_internal.step9_stt_to_tts import _AI_AGENT_UNREACHABLE_APOLOGY

    assert result.success, result.message  # the pipeline survived
    assert brain.tts.spoken == [_AI_AGENT_UNREACHABLE_APOLOGY]
    assert brain.speaker.pcm_bytes > 24000  # and the apology really came out of the real speaker
    assert not brain.stepper.results
    run(brain.close())


def test_a_real_stepper_that_is_down_does_not_change_what_is_said(fresh, speech):
    stack = fresh([s for s in ALL_SERVICES if s != "stepper"])
    brain, result = scenario(stack, speech, "Please rotate your left arm ninety degrees forward.", wait_for_move=True)

    assert result.success, result.message
    (reply,) = brain.ai_agent.replies
    assert reply.directive is not None, f"the LLM planned no movement: {reply.response!r}"
    assert brain.tts.spoken == [reply.response.strip()]
    assert brain.speaker.pcm_bytes > 24000
    assert brain.stepper.errors and not brain.stepper.results  # the move was attempted and failed alone
    run(brain.close())
