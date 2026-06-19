# 🎓 Saathi AI Teacher

An AI-powered teaching assistant for school students, built with Streamlit. Ask any question and get a structured lesson with explanation, key points, a visual aid, and a quiz — all in English, Hindi, or Hinglish.

## Features

- **Multilingual** — supports English, Hindi, and Hinglish responses
- **Voice input** — record your question using the microphone (transcribed via Faster Whisper)
- **Text-to-speech** — listen to the explanation read aloud (via Edge TTS)
- **Smartboard** — auto-generates emoji diagrams, ASCII art, or Mermaid flowcharts depending on the topic
- **Quiz** — every lesson ends with a multiple-choice question to test understanding
- **Powered by Groq** — uses `llama-3.3-70b-versatile` for fast, structured responses

## Project Structure

```
.
├── app.py            # Main Streamlit application
├── stt.py            # Speech-to-text using Faster Whisper
├── tts.py            # Text-to-speech using Edge TTS
├── requirements.txt  # Python dependencies
└── .env              # Environment variables (not committed)
```

## Setup

1. **Clone the repo and create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your Groq API key** in a `.env` file
   ```
   GROQ_API_KEY=your_key_here
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Usage

1. Type a topic or question (e.g. *"What is photosynthesis?"*) or click the mic to speak
2. Select a response language (English / Hindi / Hinglish)
3. Click **▶ Teach Me**
4. Read the explanation, view the visual on the Smartboard, and attempt the quiz
5. Click **🔊 Read Explanation** to hear the lesson aloud

## Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web UI |
| `groq` | LLM API (Llama 3.3 70B) |
| `faster-whisper` | Speech-to-text |
| `edge-tts` | Text-to-speech |
| `audio-recorder-streamlit` | In-browser mic recording |
| `streamlit-mermaid` | Mermaid diagram rendering |
| `python-dotenv` | Environment variable loading |
