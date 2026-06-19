import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import json
from tts import text_to_speech
from stt import speech_to_text
from audio_recorder_streamlit import audio_recorder
try:
    from streamlit_mermaid import st_mermaid
    MERMAID_AVAILABLE = True
except ImportError:
    MERMAID_AVAILABLE = False

st.set_page_config(page_title="Saathi AI Teacher", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")
load_dotenv()

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] { background: #0f1117; color: #e8eaf0; }
[data-testid="stSidebar"] { display: none; }
[data-testid="stAppViewContainer"] > section:first-child { display: none; }

.app-header {
    background: #161b27;
    border-bottom: 1px solid #2a3550;
    padding: 14px 28px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 0;
}
.app-header h1 { font-size: 1.4em; margin: 0; color: #e8eaf0; }

.input-bar {
    background: #161b27;
    border-bottom: 1px solid #2a3550;
    padding: 12px 28px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.panel-card {
    background: #161b27;
    border: 1px solid #2a3550;
    border-radius: 12px;
    padding: 20px;
    height: 100%;
    min-height: 360px;
}
.panel-title {
    font-size: 0.75em;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #4a6fa5;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid #2a3550;
}
.quiz-card {
    background: #161b27;
    border: 1px solid #2a3550;
    border-radius: 12px;
    padding: 20px;
    margin-top: 16px;
}

.stButton > button {
    background: #1e3a5f !important;
    color: #7eb8f7 !important;
    border: 1px solid #2a5080 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}
.stButton > button:hover { background: #2a5080 !important; color: #fff !important; }

[data-testid="stTextInput"] input {
    background: #1a2035 !important;
    border: 1px solid #2a3550 !important;
    color: #e8eaf0 !important;
    border-radius: 8px !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #1a2035 !important;
    border: 1px solid #2a3550 !important;
    color: #e8eaf0 !important;
    border-radius: 8px !important;
}
[data-testid="stRadio"] > label { font-size: 1em !important; font-weight: 600 !important; color: #a0c4ff !important; }
hr { border-color: #2a3550 !important; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
for key, default in [("current_lesson", None), ("language", "English"), ("history", [])]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Groq Client ───────────────────────────────────────────────────────────────
@st.cache_resource
def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

client = get_groq_client()
TTS_LANG = {"English": "en", "Hindi": "hi", "Hinglish": "hi"}

# ── LLM ───────────────────────────────────────────────────────────────────────
def generate_lesson(question, history, language):
    lang_instruction = (
        "Respond entirely in Hindi." if language == "Hindi"
        else "Use simple Hindi written in English script (Hinglish)." if language == "Hinglish"
        else "Respond in English."
    )
    prompt = f"""You are Saathi, an AI Teaching Assistant for school students.
Student Language: {language}
{lang_instruction}

Student Question: {question}
Conversation History: {history}

Choose the best visual:
- emoji: simple concepts (e.g. "🌿 → 🐇 → 🦊")
- ascii: labelled diagrams (e.g. plant parts)
- mermaid: flows/cycles (e.g. water cycle)

Return ONLY valid JSON:
{{
    "answer": "explanation under 120 words, short sentences, one real-life example",
    "key_points": ["point 1", "point 2", "point 3"],
    "example": "one concrete real-life example",
    "visual_type": "emoji|ascii|mermaid",
    "visual": "visual content",
    "quiz_question": "one quiz question",
    "quiz_options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "correct_answer": "A) ..."
}}"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def render_visual(visual_type, visual):
    if visual_type == "emoji":
        st.markdown(f"<div style='text-align:center;font-size:2em;line-height:2.2'>{visual}</div>", unsafe_allow_html=True)
    elif visual_type == "ascii":
        st.code(visual, language=None)
    elif visual_type == "mermaid":
        if MERMAID_AVAILABLE:
            st_mermaid(visual)
        else:
            st.code(visual, language=None)

# ════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='app-header'><h1>🎓 Saathi AI Teacher</h1></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# INPUT BAR
# ════════════════════════════════════════════════════════════════════════════
col_topic, col_lang, col_voice, col_btn = st.columns([5, 1.5, 1, 1])

with col_topic:
    topic = st.text_input("topic", placeholder="Enter a topic or question (e.g. What is photosynthesis?)",
                          label_visibility="collapsed", key="topic_input")

with col_lang:
    st.session_state.language = st.selectbox(
        "lang", ["English", "Hindi", "Hinglish"],
        index=["English", "Hindi", "Hinglish"].index(st.session_state.language),
        label_visibility="collapsed"
    )

with col_voice:
    audio_bytes = audio_recorder(text="", recording_color="#e74c3c", neutral_color="#4a6fa5", icon_size="lg")

with col_btn:
    ask_clicked = st.button("▶ Teach Me", use_container_width=True)

# Handle voice input
if audio_bytes and not st.session_state.get("_last_audio") == audio_bytes:
    st.session_state["_last_audio"] = audio_bytes
    with st.spinner("Transcribing..."):
        spoken = speech_to_text(audio_bytes)
    if spoken:
        st.session_state["_voice_topic"] = spoken
        st.rerun()

if st.session_state.get("_voice_topic"):
    topic = st.session_state.pop("_voice_topic")
    ask_clicked = True

# ── Process question ──────────────────────────────────────────────────────────
if ask_clicked and topic.strip():
    history_str = "\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.history)
    with st.spinner("Saathi is thinking..."):
        try:
            lesson = generate_lesson(topic.strip(), history_str, st.session_state.language)
        except Exception as e:
            st.error(f"Couldn't generate a lesson. Please try again. ({e})")
            st.stop()
    st.session_state.history.append({"role": "user", "content": topic.strip()})
    st.session_state.history.append({"role": "assistant", "content": lesson.get("answer", "")})
    st.session_state.current_lesson = lesson
    st.rerun()

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# MAIN PANELS — Lesson (left) | Smartboard (right)
# ════════════════════════════════════════════════════════════════════════════
left, right = st.columns(2, gap="medium")

lesson = st.session_state.current_lesson

with left:
    st.markdown("<div class='panel-title'>📚 Lesson Panel</div>", unsafe_allow_html=True)
    if lesson:
        st.markdown("**Explanation**")
        st.write(lesson.get("answer", ""))

        key_points = lesson.get("key_points", [])
        if key_points:
            st.markdown("**Key Points**")
            for pt in key_points:
                st.markdown(f"• {pt}")

        example = lesson.get("example", "")
        if example:
            st.markdown("**Example**")
            st.info(example)

        tts_lang = TTS_LANG[st.session_state.language]
        if st.button("🔊 Read Explanation", key="tts_btn"):
            st.audio(text_to_speech(lesson["answer"], tts_lang))
    else:
        st.markdown("""
        <div style='text-align:center;padding:80px 0;color:#4a6fa5'>
            <div style='font-size:2.5em'>📖</div>
            <div style='margin-top:10px'>Enter a topic above to get a lesson</div>
        </div>""", unsafe_allow_html=True)

with right:
    st.markdown("<div class='panel-title'>🖍 Smartboard</div>", unsafe_allow_html=True)
    if lesson:
        render_visual(lesson.get("visual_type", "emoji"), lesson.get("visual", ""))
    else:
        st.markdown("""
        <div style='text-align:center;padding:80px 0;color:#4a6fa5'>
            <div style='font-size:2.5em'>🖊️</div>
            <div style='margin-top:10px'>Diagram / Visual Aid will appear here</div>
        </div>""", unsafe_allow_html=True)

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# QUIZ SECTION
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='panel-title'>📝 Quiz Section</div>", unsafe_allow_html=True)

if lesson:
    q_col, spacer = st.columns([3, 1])
    with q_col:
        selected = st.radio(
            lesson["quiz_question"],
            lesson["quiz_options"],
            key=f"quiz_{len(st.session_state.history)}"
        )
        sub_col, clr_col = st.columns([1, 1])
        with sub_col:
            if st.button("✅ Submit Answer", use_container_width=True):
                if selected == lesson["correct_answer"]:
                    st.success("Correct! 🎉")
                else:
                    st.error(f"Not quite! The answer is: **{lesson['correct_answer']}**")
        with clr_col:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.current_lesson = None
                st.session_state.history = []
                st.rerun()
else:
    st.caption("Quiz will appear after you ask a question.")
