"""Launches ONE real microservice over real HTTP with fake hardware/engines.

    <service venv python> fake_services.py <microphone|stt|tts|speaker|ai_agent> <port>

Run with the service's own directory as the working directory and its own virtualenv: the code under
test is the service's real HTTP layer, application layer and composition; only the devices (sound
card, whisper, SAPI) and ai-agent's LLM are replaced. Used by ``test_voice_pipeline_wire.py`` and
``test_brain_ai_agent_flows.py``.
"""

import asyncio
import math
import os
import struct
import sys
import wave

sys.path.insert(0, os.getcwd())

import uvicorn  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from shared_logging import TracingMiddleware, current_trace_id  # noqa: E402

CAPTURE_RATE = 16000


def record_trace(service: str) -> None:
    """Note which trace the device/engine code of this service runs in (the stream's own task)."""
    directory = os.environ.get("E2E_TRACE_DIR")
    if directory:
        with open(os.path.join(directory, f"{service}.trace"), "a") as out:
            out.write((current_trace_id() or "none") + "\n")

NATIVE_TTS_RATE = 22050


def build_microphone() -> FastAPI:
    from application.ports.outbound.audio_capture_port import AudioCapturePort
    from application.ports.outbound.audio_stream_port import AudioStreamPort
    from application.services.microphone_service import MicrophoneService
    from infrastructure.inbound.http.http_handler import MicrophoneHandler

    class SineStream(AudioStreamPort):
        """A sound card with someone speaking: a moment of room noise, 80 chunks of a loud tone, then silence.

        The microphone cuts the stream into utterances, so what the pipeline gets is that one tone as one utterance.
        """

        QUIET_CHUNKS, TONE_CHUNKS = 5, 80

        def __init__(self, chunk_size: int) -> None:
            self._chunk_size, self._n, self._closed, self._chunks = chunk_size, 0, False, 0

        @property
        def sample_rate(self) -> int:
            return CAPTURE_RATE

        def __aiter__(self):
            return self

        async def __anext__(self) -> bytes:
            if self._closed:
                raise StopAsyncIteration
            await asyncio.sleep(0.01)
            record_trace("microphone")
            self._chunks += 1
            if self._chunks <= self.QUIET_CHUNKS:
                amplitude = 20  # room noise: the microphone learns its noise floor from it
            elif self._chunks <= self.QUIET_CHUNKS + self.TONE_CHUNKS:
                amplitude = 8000
            else:
                amplitude = 0
            samples = [
                int(amplitude * math.sin(2 * math.pi * 300 * (self._n + i) / CAPTURE_RATE))
                for i in range(self._chunk_size)
            ]
            self._n += self._chunk_size
            return struct.pack(f"<{self._chunk_size}h", *samples)

        def on_terminated(self, callback) -> None:
            pass

        async def close(self) -> None:
            self._closed = True

    class Capture(AudioCapturePort):
        async def open_stream(self, audio_format):
            return SineStream(audio_format.chunk_size)

    app = FastAPI()
    app.include_router(MicrophoneHandler(MicrophoneService(Capture())).router)
    return app


def build_stt() -> FastAPI:
    from application.ports.outbound.transcription_port import TranscriptionPort
    from application.services.stt_service import SttService
    from infrastructure.inbound.http.http_handler import SttHandler

    class Engine(TranscriptionPort):
        async def transcribe_batch(self, audio_data: bytes, sample_rate: int) -> str:
            record_trace("stt")
            return "hello wire" if audio_data else ""  # an utterance, cut by the microphone, reached the engine

        def is_available(self) -> bool:
            return True

    app = FastAPI()
    app.include_router(SttHandler(SttService(Engine(), "stt")).router)
    return app


def build_tts() -> FastAPI:
    from application.services.tts_service import TtsService
    from infrastructure.inbound.http.http_handler import TtsHandler
    from infrastructure.outbound.pyttsx3_speech.pyttsx3_speech_synthesis import Pyttsx3SpeechSynthesis

    class Synth:
        """Speaks 0.1 s of 22.05 kHz mono per character, like an engine with its own native rate."""

        async def synthesize_to_file(self, text: str, file_path: str) -> None:
            record_trace("tts")
            with wave.open(file_path, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(NATIVE_TTS_RATE)
                wav_file.writeframes(b"\x20\x00" * (NATIVE_TTS_RATE // 10) * len(text))

        async def is_working(self) -> bool:
            return True

    app = FastAPI()
    app.include_router(TtsHandler(TtsService(Pyttsx3SpeechSynthesis(Synth()))).router)
    return app


def build_speaker() -> FastAPI:
    from application.dtos.playback_outbound import PlaybackOutboundDTO
    from application.dtos.readiness_outbound import ReadinessOutboundDTO
    from application.ports.outbound.audio_playback_port import AudioPlaybackPort
    from application.services.speaker_service import SpeakerService
    from infrastructure.inbound.http.http_handler import SpeakerHandler

    sink = os.environ["E2E_SPEAKER_SINK"]

    class Playback(AudioPlaybackPort):
        """A 'device' that records the requested format and every byte it is asked to play."""

        async def play(self, audio_format, audio_stream, on_started):
            record_trace("speaker")
            with open(sink + ".format", "w") as fmt:
                fmt.write(f"{audio_format.sample_rate},{audio_format.channels}")
            on_started(PlaybackOutboundDTO(success=True, message="Playback stream started"))
            async for chunk in audio_stream:
                with open(sink, "ab") as out:
                    out.write(chunk)
            return PlaybackOutboundDTO(success=True, message="Playback session finalized successfully")

        async def close(self) -> None:
            return None

        async def check_readiness(self) -> ReadinessOutboundDTO:
            return ReadinessOutboundDTO(is_ready=True)

        def is_playing(self) -> bool:
            return False

    app = FastAPI()
    app.include_router(SpeakerHandler(SpeakerService(Playback(), "speaker")).router)
    return app


def build_ai_agent() -> FastAPI:
    """ai-agent through its REAL composition root (router, flows, routes, sessions, tracing); only the LLM is replaced.

    The replacement answers by the keywords of the user's message, so the flows can be driven without a provider.
    Triage sends a message about an arm ("arm", "move", "turn") to the movement flow, one about a table to the
    special flow and everything else to the conversation flow. The movement flow plans "there and back" (left 90, then
    left -90), asks "how many degrees" when asked to "move my arm" and refuses "too far"; the draft says whether the
    message was planned ("PLANNED", special flow) or not ("PLAIN", conversation flow).
    ``/_e2e/formats`` lists the LLM calls the service made (which phases ran) and ``/_e2e/reset`` forgets them.
    """
    import re

    from application.outbound.ports.llm_ports import LLMOutboundPort
    from infrastructure.outbound.llm import vercel
    from infrastructure.outbound.llm.response_mapper import build_response

    usage = {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}
    steady_next_step = {"ready_to_execute": True, "status": "complete", "recommended_action": "",
                        "blocking_reason": "", "requested_user_input": []}

    class KeywordLLM(LLMOutboundPort):
        def __init__(self) -> None:
            self.formats: list[str] = []
            self.draft = ""

        def is_available(self) -> bool:
            return True

        @staticmethod
        def _current_and_answers(text: str) -> str:
            """The user's current message and the answers the user gave when asked: never the earlier turns."""
            current = text.split("Current user message:\n", 1)[-1]
            current, _, answers = current.partition("\n\nInformation the user gave when asked:")
            return (current + " " + answers).lower()

        def ask(self, payload):
            fmt = payload.response_format.name if payload.response_format else "<text>"
            self.formats.append(fmt)
            text = payload.message.content
            if fmt == "<text>":  # phase 99: the question for the user
                return build_response("Which arm, and how many degrees?", usage)
            if fmt == "triage_specialist_phase1_response_format":
                heard = self._current_and_answers(text)
                domain = ("movement" if any(word in heard for word in ("arm", "move", "turn", "rotate", "raise", "lift"))
                          else "writing" if any(word in heard for word in ("table", "report", "essay", "plan", "list"))
                          else "communication")
                return build_response({
                    "intent": {"primary": "information_request", "secondary": [], "confidence": 0.9},
                    "user_goal": {"summary": "goal", "expected_outcome": "outcome"},
                    "task_category": {"domain": domain, "type": "generation", "complexity": "low"},
                    "next_step": {**steady_next_step, "status": "proceed", "recommended_action": "plan"},
                }, usage)
            if fmt == "project_manager_phase2_response_format":
                return build_response({
                    "actions": [{"id": "1", "description": "write the table", "action_type": "generation",
                                 "dependencies": [], "required_inputs": [], "output": "", "error": "",
                                 "mcp_context": {"server_id": "", "tool_name": "", "parameters": {}}}],
                    "next_step": {**steady_next_step, "status": "proceed"}, "task_category_complexity": "low"}, usage)
            if fmt == "safety_quality_gatekeeper_phase3_response_format":
                return build_response({"safety_and_validation": {"sensitive": False, "requires_confirmation": False},
                                       "next_step": {**steady_next_step, "status": "proceed"}}, usage)
            if re.match(r"phase\d_single_action_response_format", fmt):
                action_id = re.search(r"Action\(id=Id\(value='([^']+)'\)", text)
                return build_response({"actions": [{
                    "id": action_id.group(1) if action_id else "1", "description": "d", "action_type": "generation",
                    "dependencies": [], "required_inputs": [], "error": "", "output": "the table",
                    "mcp_context": {"server_id": "", "tool_name": "", "parameters": {}}}]}, usage)
            if fmt == "emotion_reader_phase30_response_format":
                heard = text.lower()
                emotion, intensity = (("joy", 4) if any(word in heard for word in ("puppy", "wonderful", "happy"))
                                      else ("sadness", 3) if any(word in heard for word in ("sad", "lost", "died"))
                                      else ("calm", 2))
                return build_response({"emotion": emotion, "intensity": intensity, "improvised": []}, usage)
            if fmt == "motion_planner_phase20_response_format":
                heard = self._current_and_answers(text)
                if "too far" in heard:
                    moves = [("left", 9999, "forward")]
                elif "there and back" in heard:
                    moves = [("left", 90, "forward"), ("left", -90, "forward")]
                elif "30 degrees" in heard:
                    moves = [("left", 30, "forward")]
                elif "move my arm" in heard:
                    return build_response({"is_motion_request": True, "movements": [], "spoken_reply": "", "next_step": {
                        "ready_to_execute": False, "status": "awaiting_user_input",
                        "recommended_action": "ask_user_for_missing_information", "blocking_reason": "details missing",
                        "requested_user_input": ["Which arm, and how many degrees?"]}}, usage)
                elif "left" in heard or "right" in heard:       # any other request that names an arm
                    arm = "left" if "left" in heard else "right"
                    moves = [(arm, 90, "forward")] + ([(arm, -90, "forward")] if "back" in heard else [])
                else:
                    return build_response({"is_motion_request": False, "movements": [],
                                           "spoken_reply": "I can only move my arms.",
                                           "next_step": steady_next_step}, usage)
                return build_response({"is_motion_request": True, "next_step": steady_next_step,
                                       "spoken_reply": "Moving my left arm.", "movements": [
                    {"arm": arm, "degrees": degrees, "direction": direction} for arm, degrees, direction in moves]}, usage)
            if fmt == "answer_checker_phase9_response_format":
                reply = re.search(r"'user_reply': '([^']*)'", text)
                return build_response({"verdict": "answered", "answer": reply.group(1) if reply else "",
                                       "message_to_user": ""}, usage)
            if fmt == "draft_writer_phase7_response_format":
                self.draft = "PLAIN" if "'actions': None" in text else "PLANNED"
                return build_response({"user_goal": {"summary": "s", "expected_outcome": self.draft}}, usage)
            if fmt == "editor_in_chief_phase8_response_format":
                return build_response({"user_goal": {"summary": "s", "expected_outcome": self.draft},
                                       "next_step": steady_next_step}, usage)
            raise AssertionError(f"unexpected response format: {fmt}")

    llm = KeywordLLM()
    vercel.VercelAIAdapter = lambda Config: llm  # before composition_root.main binds the name
    from composition_root import main as composition_root

    @composition_root.app.get("/_e2e/formats")
    async def formats():
        return llm.formats

    @composition_root.app.get("/_e2e/reset")
    async def reset():
        llm.formats.clear()
        return {"ok": True}

    return composition_root.app


BUILDERS = {"microphone": build_microphone, "stt": build_stt, "tts": build_tts, "speaker": build_speaker,
            "ai_agent": build_ai_agent}

if __name__ == "__main__":
    name, port = sys.argv[1], int(sys.argv[2])
    app = BUILDERS[name]()
    if name != "ai_agent":  # ai-agent's own composition root already added it
        app.add_middleware(TracingMiddleware)  # as every real composition root does
    uvicorn.run(app, host="127.0.0.1", port=port, log_config=None, access_log=False)
