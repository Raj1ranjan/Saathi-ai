import tempfile
import os
import streamlit as st
from faster_whisper import WhisperModel


# Whisper model loads only when first needed
@st.cache_resource
def get_whisper_model():
    return WhisperModel(
        "base",
        device="cpu",
        compute_type="int8"
    )


def speech_to_text(audio_bytes):

    model = get_whisper_model()

    audio_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as f:
            f.write(audio_bytes)
            audio_path = f.name

        segments, _ = model.transcribe(audio_path)

        transcript = " ".join(
            segment.text for segment in segments
        ).strip()

        return transcript

    finally:
        # Remove temporary audio file
        if audio_path and os.path.exists(audio_path):
            os.unlink(audio_path)