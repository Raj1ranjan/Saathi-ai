from faster_whisper import WhisperModel
import tempfile

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)


def speech_to_text(audio_bytes):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ) as f:

        f.write(audio_bytes)
        audio_path = f.name

    segments, _ = model.transcribe(audio_path)

    transcript = ""

    for segment in segments:
        transcript += segment.text + " "

    return transcript.strip()