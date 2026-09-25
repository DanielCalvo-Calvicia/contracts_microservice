"""Synthesizes a phrase with the real Windows SAPI voice into a WAV file: the test's input data.

    <tts venv python> make_speech.py "<text>" <out.wav>

Uses SAPI directly (synchronous, through pywin32) and an English voice: pyttsx3's save_to_file
returns before SAPI has written anything (the file stays a bare header when the process exits at once),
and the machine's default voice may be another language while whisper is configured for English.
"""

import sys

import win32com.client

text, out = sys.argv[1], sys.argv[2]
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
