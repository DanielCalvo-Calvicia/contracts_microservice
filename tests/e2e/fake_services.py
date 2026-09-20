"""Launches ONE real microservice over real HTTP with fake hardware/engines.

    <service venv python> fake_services.py <microphone|stt|tts|speaker> <port>

Run with the service's own directory as the working directory and its own virtualenv: the code under
test is the service's real HTTP layer, application layer and composition; only the devices (sound
card, whisper, SAPI) are replaced. Used by ``test_voice_pipeline_wire.py``.
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
        def __init__(self, chunk_size: int) -> None:
            self._chunk_size, self._n, self._closed = chunk_size, 0, False

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
            samples = [
                int(8000 * math.sin(2 * math.pi * 300 * (self._n + i) / CAPTURE_RATE))
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
        async def transcribe_stream(self, settings, audio_stream):
            async def texts():
                chunks = 0
                async for chunk in audio_stream:
                    chunks += len(chunk) > 0
                    record_trace("stt")
                    if chunks == 8:  # the microphone's audio reached the engine
                        yield "hello wire"

            return texts()

        async def transcribe_batch(self, audio_data: bytes, sample_rate: int) -> str:
            return ""

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


BUILDERS = {"microphone": build_microphone, "stt": build_stt, "tts": build_tts, "speaker": build_speaker}

if __name__ == "__main__":
    name, port = sys.argv[1], int(sys.argv[2])
    app = BUILDERS[name]()
    app.add_middleware(TracingMiddleware)  # as every real composition root does
    uvicorn.run(app, host="127.0.0.1", port=port, log_config=None, access_log=False)
