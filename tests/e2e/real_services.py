"""Launches ONE real microservice exactly as it runs in production (its own main.py / composition
root, its own real engine: whisper, SAPI, sounddevice playback, the real LLM provider, the stepper's
own mock-hardware mode).

    <service venv python> real_services.py <microphone|stt|tts|speaker|ai_agent|stepper>

Run with the service's own directory as the working directory and its own virtualenv. The ONLY
substitution is the microphone's input data: its capture device (sound card) is replaced by a WAV
file streamed in real time, followed by silence, so a spoken phrase arrives as if someone said it.
Used by ``test_real_pipeline.py``.
"""

import asyncio
import math
import os
import runpy
import sys
import wave

sys.path.insert(0, os.getcwd())


def _run_microphone() -> None:
    import numpy as np
    from application.ports.outbound.audio_capture_port import AudioCapturePort
    from application.ports.outbound.audio_stream_port import AudioStreamPort
    from composition_root.dependencies import microphone_dependencies as deps
    from main_flow.http import run_http

    wav_path = os.environ["E2E_MIC_WAV"]
    lead_in_seconds = 0.5

    class WavStream(AudioStreamPort):
        """The recorded phrase, paced like a live microphone, then silence until closed."""

        def __init__(self, sample_rate: int, chunk_size: int) -> None:
            self._rate, self._chunk, self._closed, self._position = sample_rate, chunk_size, False, 0
            with wave.open(wav_path, "rb") as wav:  # re-read on every open: a test may swap the file
                frames = np.frombuffer(wav.readframes(wav.getnframes()), dtype=np.int16).astype(np.float32)
                channels, source_rate = wav.getnchannels(), wav.getframerate()
            if channels > 1:
                frames = frames.reshape(-1, channels).mean(axis=1)
            target_length = int(len(frames) * sample_rate / source_rate)
            positions = np.linspace(0, len(frames) - 1, target_length)
            speech = np.interp(positions, np.arange(len(frames)), frames).astype(np.int16)
            self._samples = np.concatenate([np.zeros(int(lead_in_seconds * sample_rate), dtype=np.int16), speech])

        @property
        def sample_rate(self) -> int:
            return self._rate

        def __aiter__(self):
            return self

        async def __anext__(self) -> bytes:
            if self._closed:
                raise StopAsyncIteration
            await asyncio.sleep(self._chunk / self._rate)  # real time, like a sound card
            chunk = self._samples[self._position : self._position + self._chunk]
            self._position += self._chunk
            if len(chunk) < self._chunk:
                chunk = np.concatenate([chunk, np.zeros(self._chunk - len(chunk), dtype=np.int16)])
            return chunk.tobytes()

        def on_terminated(self, callback) -> None:
            pass

        async def close(self) -> None:
            self._closed = True

    class WavCapture(AudioCapturePort):
        async def open_stream(self, audio_format):
            return WavStream(audio_format.sample_rate, audio_format.chunk_size)

    deps.new_audio_capture = lambda cfg: WavCapture()
    asyncio.run(run_http())


def _run_main(path: str) -> None:
    runpy.run_path(path, run_name="__main__")


if __name__ == "__main__":
    service = sys.argv[1]
    if service == "microphone":
        _run_microphone()
    elif service == "ai_agent":
        _run_main(os.path.join("composition_root", "main.py"))
    else:
        _run_main("main.py")
