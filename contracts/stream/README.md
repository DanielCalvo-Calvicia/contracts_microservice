# contracts.stream

The messages the OBLIVION microservices exchange on their long-lived streams. **This package is the
single source of truth**: a service never defines its own copy of an event, and never hand-writes the
JSON of one. Use the classes for the event, `contracts.stream.codec` for bytes, and
`contracts.stream.schemas` for "which events may this stream carry".

## Topology

Brain is the only coordinator. A service talks to Brain and to nobody else.

```text
Microphone --MICROPHONE_OUTBOUND--> Brain --STT_INBOUND----> STT
                                    Brain <--STT_OUTBOUND---- STT
                                    Brain --TTS_INBOUND----> TTS
                                    Brain <--TTS_OUTBOUND---- TTS
                                    Brain --SPEAKER_INBOUND-> Speaker
                                    Brain <--SPEAKER_OUTBOUND- Speaker   (playback result)
```

Stepper has `STEPPER_INBOUND`/`STEPPER_OUTBOUND` schemas, used by its stream route (`/process/stream/{id}/set`): the
sender streams `stream_started` (`stepper_id`) and one `partial` per motor command (`rotate`, `steps` or `stop`), and the
stepper answers with `stream_started`, one `partial` result per command (`action`, `success`, `message`) and `completed`.
Brain currently drives the motors through the batch `/control/{id}/...` calls instead.

Each arrow is one HTTP request/response whose body is an event stream, so the W3C `traceparent`
header of Brain's request covers the whole life of the stream (no trace id lives in the event).

## Envelope (`BaseEvent`)

| field       | rule |
|-------------|------|
| `type`      | `stream_started` \| `partial` \| `utterance` \| `completed` \| `input_completed` \| `heartbeat` \| `error` |
| `sequence`  | 1, 2, 3, … per stream and direction, no gaps |
| `timestamp` | UTC ISO-8601 with microseconds and a trailing `Z` |
| `payload`   | always a JSON object (`{}` for `stream_started`/`heartbeat` without data) |

Framing: NDJSON (one object per line) or Server-Sent Events (`data: <json>` + blank line). Both carry
identical events. STT answers with SSE by default and NDJSON on `Accept: application/x-ndjson`; every
other stream is NDJSON.

## Lifecycle

```text
stream_started -> (partial | utterance | heartbeat)* -> completed ... -> end of body
                                  \-> error (recoverable=true: keep reading; false: the stream is over)
```

* `input_completed` (`reason`, default `end_of_input`) is what STT and TTS answer on an upload request once the sender
  ended its stream (schema `UPLOAD_ACK`); it is not a unit boundary of the data stream.
* `stream_started` is first and sent once. The receiver rejects anything else first.
* `completed` closes one *unit* (an utterance, a spoken text, a playback), not necessarily the stream:
  STT, TTS and Brain's text stream carry several units, each ending in its own `completed`.
* `error` with `recoverable=false`, or a body that ends without the expected `completed`, fails the
  stream. The consumer's cancellation (closing the connection) cancels the producer's work.
* A consumer that breaks the rules gets an `error` event back (uploads) or an error (downloads); it is
  never silently repaired.

## Audio

Every `bytes_base64` is raw little-endian PCM16. The rate is fixed by whoever produces it and never
converted in between:

| stream | format |
|--------|--------|
| Microphone → Brain → STT | mono, one `utterance` event per finished utterance (the microphone does the silence cutting) at the rate in that event (the microphone's rate, or the one it was asked to resample to; default 16 kHz) |
| TTS → Brain → Speaker    | mono, the rate Brain asked TTS for (default 24 kHz); TTS converts from its engine's rate |
| Speaker device           | the speaker resamples only if its device rejects that rate, and logs that it did |

## Changing a contract

Add optional fields rather than changing existing ones: the codec ignores unknown payload fields, so
additions are backward compatible. Removing or retyping a field, or adding a required one, needs a
version bump of `contracts-microservice` and every service updated together.
