"""Deprecated location; kept so existing imports keep working.

The event lives with its owner: ``microphone.outbound.stream_started`` and
``speaker.outbound.stream_started``.
"""
from contracts.stream.microservices.microphone.outbound.stream_started import (  # noqa: F401
    MicrophoneStreamStartedEvent,
    MicrophoneStreamStartedEventDTO,
)
