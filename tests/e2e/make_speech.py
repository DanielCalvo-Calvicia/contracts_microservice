"""Synthesizes a phrase into a WAV file: the test's input data.

    <tts venv python> make_speech.py "<text>" <out.wav>

On Windows it uses the real SAPI voice directly (synchronous, through pywin32) and an English voice: pyttsx3's
save_to_file returns before SAPI has written anything (the file stays a bare header when the process exits at once),
and the machine's default voice may be another language while whisper is configured for English.

Where pywin32 is not available (Linux, Raspberry Pi) it uses the Piper voice that tts_microservice ships
(models/<voice>.onnx, fetched by tts_microservice/scripts/fetch_voice.py). TTS_PIPER_VOICE picks another voice.
"""

import os
import sys
import wave
from pathlib import Path

DEFAULT_VOICE = "en_GB-alan-medium"
TTS_MODEL_DIR = Path(__file__).resolve().parents[3] / "tts_microservice" / "models"


def speak_with_sapi(text: str, out: str) -> None:
    import win32com.client  # noqa: PLC0415 (Windows only)

    voice = win32com.client.Dispatch("SAPI.SpVoice")
    voices = voice.GetVoices()
    for index in range(voices.Count):
        if "english" in voices.Item(index).GetDescription().lower():
            voice.Voice = voices.Item(index)
            break
    stream = win32com.client.Dispatch("SAPI.SpFileStream")
    stream.Open(out, 3)  # SSFMCreateForWrite
    voice.AudioOutputStream = stream
    voice.Speak(text)  # synchronous: returns when the audio is written
    stream.Close()


def speak_with_piper(text: str, out: str) -> None:
    from piper import PiperVoice  # noqa: PLC0415 (installed in the tts virtualenv)

    voice_name = os.environ.get("TTS_PIPER_VOICE", DEFAULT_VOICE)
    model = TTS_MODEL_DIR / f"{voice_name}.onnx"
    if not model.is_file():
        sys.exit(f"Piper voice not found: {model} (run tts_microservice/scripts/fetch_voice.py)")
    voice = PiperVoice.load(model)
    with wave.open(out, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)


def main() -> None:
    text, out = sys.argv[1], sys.argv[2]
    if sys.platform == "win32":
        try:
            speak_with_sapi(text, out)
            return
        except ImportError:  # no pywin32 in this virtualenv: the Piper voice is the portable path
            pass
    speak_with_piper(text, out)


if __name__ == "__main__":
    main()
