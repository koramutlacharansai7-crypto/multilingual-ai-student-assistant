
import streamlit as st
import os
import requests
from dotenv import load_dotenv

from gnani.tts import GnaniTTSClient
from streamlit_mic_recorder import mic_recorder

# Load environment variables
load_dotenv(override=True)

# Streamlit page settings

st.markdown("""
<style>
    .stApp {
        background-color: #f4f7fb;
    }

    .block-container {
        max-width: 1000px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1 {
        color: #173b70;
        font-weight: 800;
    }

    h2, h3 {
        color: #24558a;
    }

    div.stButton > button {
        background-color: #2458a6;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 1rem;
        font-weight: 600;
    }

    div.stButton > button:hover {
        background-color: #173b70;
        color: white;
        border: none;
    }

    div[data-testid="stSelectbox"] {
        background-color: white;
        border-radius: 10px;
    }

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Gnani AI Student Assistant",
    page_icon="🎓",
    layout="centered"
)

# Gnani API details
GNANI_API_URL = "https://api.vachana.ai/stt/v3"
GNANI_API_KEY = os.getenv("GNANI_API_KEY")

# Gemini API details
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


## Gemini AI answer function using REST API
# Gemini AI answer function using REST API
def generate_ai_answer(question):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-flash-lite-latest:generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
    "text": (
        f"Answer the following student question in "
        f"{st.session_state.get('selected_language', 'English')}. "
        f"Use simple, clear language.\n\n"
        f"Student question: {question}"
    )
}
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 300
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=60
    )

    if response.status_code != 200:
        raise Exception(
            f"Status: {response.status_code}\nGoogle response: {response.text}"
        )

    result = response.json()

    return result["candidates"][0]["content"]["parts"][0]["text"]

# Speech-to-Text function
def transcribe_audio(audio_bytes):
    headers = {
        "X-API-Key-ID": GNANI_API_KEY.strip()
    }

    files = {
        "audio_file": ("recording.wav", audio_bytes, "audio/wav")
    }

    language_codes = {
        "English": "en-IN",
        "Tamil": "ta-IN",
        "Telugu": "te-IN",
        "Hindi": "hi-IN"
    }

    selected_language = st.session_state.get(
        "selected_language", "English"
    )
    language_code = language_codes.get(
        selected_language, "en-IN"
    )

    payload = {
        "language_code": language_code,
        "preferred_language": language_code,
        "format": "transcribe"
    }

    response = requests.post(
        GNANI_API_URL,
        headers=headers,
        files=files,
        data=payload,
        timeout=60
    )

    if not response.ok:
        raise requests.RequestException(
            f"STT failed ({response.status_code}): {response.text}"
        )

    return response.json()

# Text-to-Speech function
def generate_speech(text):
    client = GnaniTTSClient(api_key=GNANI_API_KEY)

    language_settings = {
        "English": {"language": "en-IN", "voice": "Kaveri"},
        "Tamil": {"language": "ta-IN", "voice": "Kaveri"},
        "Telugu": {"language": "te-IN", "voice": "Kaveri"},
        "Hindi": {"language": "hi-IN", "voice": "Kaveri"}
    }

    selected_language = st.session_state.get(
        "selected_language", "English"
    )

    settings = language_settings.get(
        selected_language, language_settings["English"]
    )

    audio = client.synthesize(
        text=text,
        voice=settings["voice"],
        model="timbre-v2.5",
        language=settings["language"]
    )

    return audio


# Main application

st.title("🎓 Multilingual AI Student Assistant")

selected_language = st.selectbox(
    "🌐 Choose your language",
    ["English", "Tamil", "Telugu", "Hindi"],
    key="selected_language"
)


st.markdown("""
Your personal AI companion for learning, career guidance, and internships.

""")

st.info(
    "🌐 Languages: English, Tamil, Telugu, and Hindi\n\n"
    "🎙️ Voice input and speech output\n\n"
    "🤖 AI-powered answers for studies, AI, careers, and internships"
)

name = st.text_input("Enter your name")

if not GNANI_API_KEY:
    st.warning("Gnani API key not found. Please check your .env file.")
    


# Voice recording section
st.subheader("🎤 Ask using your voice")

audio = mic_recorder(
    start_prompt="Start Recording",
    stop_prompt="Stop Recording",
    format="wav",
    key="voice_recorder"
)

if audio:
    st.audio(audio["bytes"], format="audio/wav")
    st.success("Voice recording captured!")

    if st.button("Convert Voice to Text"):
        if not GNANI_API_KEY:
            st.error("API key not found. Check your .env file.")
        else:
            try:
                with st.spinner("Gnani Prisma is transcribing your voice..."):
                    result = transcribe_audio(audio["bytes"])

                if result.get("success"):
                    transcript = result.get("transcript", "").strip()

                    if transcript:
                        st.session_state["voice_question"] = transcript
                        st.success("Voice converted to text!")
                        st.write("Your spoken question:", transcript)

                        with st.spinner("Gemini is generating your answer..."):
                            answer = generate_ai_answer(transcript)

                        st.session_state["ai_answer"] = answer
                        st.divider()
                        st.markdown("### 💡 Your Personalized Response")
                        st.subheader("🤖 AI Answer")
                        st.write(answer)

                        if st.button("🔊 Listen to AI Answer", key="voice_answer_button"):
                            try:
                                with st.spinner("Gnani is generating speech..."):
                                    speech_audio = generate_speech(answer)

                                st.audio(speech_audio, format="audio/wav")
                                st.success("Speech generated successfully!")

                            except Exception as e:
                                st.error(f"Speech generation failed: {e}")

                    else:
                        st.warning("No speech detected. Please record again.")
                else:
                    st.error("Transcription failed. Please try again.")

            except requests.RequestException as e:
                st.error(f"STT error: {e}")

            except Exception as e:
                st.error(f"Voice-to-AI processing failed: {e}")
# Student question section
st.subheader("💬 Ask your question")

question = st.text_area(
    "What would you like help with?",
    value=st.session_state.get("voice_question", ""),
    placeholder="Type your question here..."
)

if st.button("Submit Question"):
    if question.strip():
        try:
            with st.spinner("Generating AI answer..."):
                answer = generate_ai_answer(question)

            st.subheader("🤖 AI Answer")
            st.write(answer)

            st.session_state["ai_answer"] = answer

        except Exception as e:
            st.error(f"AI answer generation failed: {e}")

    else:
        st.warning("Please enter or record a question.")

# Text-to-Speech testing section
# Listen to AI Answer
if "ai_answer" in st.session_state:
    st.subheader("🤖 AI Answer")

    # Keep the answer visible
    st.write(st.session_state["ai_answer"])

    if st.button("🔊 Listen to AI Answer", key="listen_saved_answer"):
        try:
            with st.spinner("Gnani is generating speech..."):
                speech_audio = generate_speech(
                    st.session_state["ai_answer"]
                )

            st.audio(speech_audio, format="audio/wav")
            st.success("Speech generated successfully!")

        except Exception as e:
            st.error(f"Speech generation failed: {e}")