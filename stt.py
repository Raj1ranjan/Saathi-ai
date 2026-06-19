import tempfile
import os
import streamlit as st
from faster_whisper import WhisperModel


@st.cache_resource
def get_whisper_model():
    return WhisperModel("base", device="cpu", compute_type="int8")


def speech_to_text(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        audio_path = f.name

    segments, _ = get_whisper_model().transcribe(audio_path)
    transcript = " ".join(segment.text for segment in segments).strip()
    os.unlink(audio_path)
    return transcript
