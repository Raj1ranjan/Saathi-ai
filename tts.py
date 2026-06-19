import asyncio
import tempfile
import os
import nest_asyncio
import streamlit as st
import edge_tts

nest_asyncio.apply()

VOICE_MAP = {
    "en": "en-IN-NeerjaNeural",
    "hi": "hi-IN-SwaraNeural",
}


@st.cache_data(show_spinner=False)
def text_to_speech(text, lang="en"):
    voice = VOICE_MAP.get(lang, VOICE_MAP["en"])
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file.close()

    async def _generate():
        await edge_tts.Communicate(text=text, voice=voice).save(temp_file.name)

    asyncio.run(_generate())

    audio_bytes = open(temp_file.name, "rb").read()
    os.unlink(temp_file.name)
    return audio_bytes
