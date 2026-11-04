import os
import base64
import io
import json
import wave

import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit_mic_recorder import speech_to_text
from gnani.tts import GnaniTTSClient, AudioConfig
from supabase import create_client

# --------------------------------------------------
# 1. Page configuration and environment
# --------------------------------------------------

st.set_page_config(
    page_title="Multilingual AI Student Assistant",
    page_icon="🎓",
    layout="centered",
)

load_dotenv(override=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GNANI_API_KEY = os.getenv("GNANI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase URL or key is missing from your .env file.")
    st.stop()

if "supabase" not in st.session_state:
    st.session_state.supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
    )

supabase = st.session_state.supabase

# Restore the logged-in student's access token for RLS-protected queries.
if st.session_state.get("access_token"):
    supabase.postgrest.auth(st.session_state.access_token)

# --------------------------------------------------
# 2. Student signup and login
# --------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if st.session_state.user is None:
    st.title("🔐 Login / Sign Up")
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #123b70, #2878c8);
            padding: 25px;
            border-radius: 16px;
            text-align: center;
            color: white;
        ">
            <h1 style="color: white;">
                🎓 Multilingual AI Student Assistant
            </h1>
            <p>Your personal AI learning companion</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Student Login / Signup")
    st.caption("Sign in to continue your learning journey.")
    st.divider()
    
    # Login form styling
    st.markdown(
        """
        <style>
        div[data-testid="stTextInput"] label {
            color: #163b70;
            font-weight: 600;
        }

        div[data-testid="stTextInput"] input {
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            padding: 10px;
            background-color: #ffffff;
        }

        div.stButton > button {
            width: 100%;
            min-height: 45px;
            border-radius: 10px;
            background-color: #2458a6;
            color: #ffffff;
            border: none;
            font-weight: 600;
        }

        div.stButton > button:hover {
            background-color: #173f7a;
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Choose login or signup
    auth_choice = st.radio(
        "Choose an option",
        ["Login", "Sign up"],
        horizontal=True,
    )
    

    email = st.text_input("Email address")
    password = st.text_input("Password", type="password")

    # Signup
    if auth_choice == "Sign up":

        if st.button("Create account"):

            if not email.strip() or not password:
                st.warning("Enter your email address and password.")

            else:
                try:
                    result = supabase.auth.sign_up(
                        {
                            "email": email.strip(),
                            "password": password,
                        }
                    )

                    if result.session and result.user:
                        st.session_state.user = result.user
                        st.session_state.access_token = (
                            result.session.access_token
                        )

                        st.success("Account created and logged in.")
                        st.rerun()

                    elif result.user:
                        st.success(
                            "Account created. Check your email if "
                            "email confirmation is required, then log in."
                        )

                    else:
                        st.error(
                            "Signup did not return a user. Please try again."
                        )

                
                except Exception as error:
                    st.error(f"Signup failed: {error}")

    # Login
    else:

        if st.button("Login"):

            if not email.strip() or not password:
                st.warning("Enter your email address and password.")
                
            else:
                try:
                    result = supabase.auth.sign_in_with_password(
                        {
                            "email": email.strip(),
                            "password": password,
                        }
                    )

                    st.session_state.user = result.user
                    st.session_state.access_token = (
                        result.session.access_token
                    )

                    st.success("Login successful!")
                    st.rerun()

                except Exception:
                    st.error(
                        "Login failed. Please check your email and "
                        "password, then try again."
                    )

    st.stop()

# --------------------------------------------------
# 2. Modern Professional Dashboard Styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    /* Main application background */
    .stApp {
        background: #f4f7fc;
        color: #1e293b;
    }

    /* Main content layout */
    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Main headings */
    h1 {
        color: #163b70;
        font-weight: 800;
        letter-spacing: -0.8px;
    }

    h2, h3 {
        color: #24558a;
        font-weight: 700;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #163b70;
    }

    /* Buttons */
    div.stButton > button {
        background: #2458a6;
        color: #ffffff;
        border: 1px solid #2458a6;
        border-radius: 10px;
        padding: 0.65rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        background: #173f7a;
        border-color: #173f7a;
        color: #ffffff;
    }

    /* Text fields and dropdowns */
    div[data-baseweb="input"],
    div[data-baseweb="textarea"],
    div[data-baseweb="select"] {
        border-radius: 10px;
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {
        border-radius: 10px;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: #ffffff;
        border: 1px solid #e5eaf2;
        border-radius: 14px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }

    /* File upload area */
    [data-testid="stFileUploader"] {
        background: #ffffff;
        border: 1px dashed #9db5d4;
        border-radius: 12px;
        padding: 0.8rem;
    }

    /* Dividers */
    hr {
        border-color: #e2e8f0;
    }

    /* Captions */
    .stCaption {
        color: #64748b;
    }

    /* Responsive layout */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)
#---------------------------------------------------
# 4. Gemini text chat
# --------------------------------------------------

def generate_ai_answer(question, language):
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing from your .env file.")

    prompt = (
        "You are Multilingual AI, a helpful student tutor. "
        f"Answer the student's question in {language}. "
        "Use simple language, clear steps, and examples when helpful. "
        "If the question is about studies, explain it for a college student. "
        f"Student's question: {question}"
    )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-flash-lite-latest:generateContent"
    )

    response = requests.post(
        url,
        params={"key": GEMINI_API_KEY},
        json={
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {"maxOutputTokens": 700},
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()

    try:
        answer = "\n".join(
            part["text"]
            for part in data["candidates"][0]["content"]["parts"]
            if "text" in part
        ).strip()
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError(
            "Gemini returned an unexpected response. Check the model/API response."
        ) from error

    if not answer:
        raise RuntimeError("Gemini returned an empty answer.")

    return answer

# --------------------------------------------------
# 5. Gnani text-to-speech
# --------------------------------------------------

def generate_speech(text, language="English"):
    if not GNANI_API_KEY:
        raise RuntimeError("GNANI_API_KEY is missing.")

    if not text or not text.strip():
        raise ValueError("There is no text to convert to speech.")

    language_codes = {
        "English": "en-IN",
        "Telugu": "te-IN",
        "Tamil": "ta-IN",
        "Hindi": "hi-IN",
        "Kannada": "kn-IN",
        "Malayalam": "ml-IN",
    }

    # Split long answers into chunks of at most 220 characters.
    chunks = []
    current = ""

    for word in text.strip().split():
        if current and len(current) + len(word) + 1 > 220:
            chunks.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()

    if current:
        chunks.append(current)

    client = GnaniTTSClient(api_key=GNANI_API_KEY)
    audio_segments = []

    for chunk in chunks:
        audio = client.synthesize(
            text=chunk,
            voice="Kaveri",
            model="timbre-v2.5",
            language=language_codes.get(language, "en-IN"),
            audio_config=AudioConfig(
                container="wav",
                sample_rate=48000,
            ),
        )

        if not audio:
            raise RuntimeError("Gnani returned empty audio.")

        audio_segments.append(audio)

    # Combine WAV chunks into one playable WAV file.
    output = io.BytesIO()

    with wave.open(output, "wb") as combined:
        for index, segment in enumerate(audio_segments):
            with wave.open(io.BytesIO(segment), "rb") as part:
                if index == 0:
                    combined.setnchannels(part.getnchannels())
                    combined.setsampwidth(part.getsampwidth())
                    combined.setframerate(part.getframerate())
                    combined.setcomptype(
                        part.getcomptype(),
                        part.getcompname(),
                    )
                elif (
                    part.getnchannels() != combined.getnchannels()
                    or part.getsampwidth() != combined.getsampwidth()
                    or part.getframerate() != combined.getframerate()
                ):
                    raise RuntimeError(
                        "Gnani returned incompatible audio formats."
                    )

                combined.writeframes(part.readframes(part.getnframes()))

    return output.getvalue()

#---------------------------------------------------
# 6. Photo and PDF question solver
# --------------------------------------------------

def generate_file_answer(uploaded_file, question, language, task):
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing from your .env file."
        )

    file_bytes = uploaded_file.getvalue()
    mime_type = uploaded_file.type

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "application/pdf",
    }

    if mime_type not in allowed_types:
        raise RuntimeError("Upload a JPG, PNG, WEBP, or PDF file.")

    if len(file_bytes) > 10 * 1024 * 1024:
        raise RuntimeError("Please upload a file smaller than 10 MB.")

    prompt = f"""
You are Multilingual AI, a helpful student tutor.
Answer in {language}.
Use the uploaded document as your main source.
Explain clearly in simple, student-friendly language.
Do not invent information that is not supported by the document.

Task: {task}

Student's question or topic: {question or "Not specified"}

For summarization, summarize the main ideas and important details.
For key-point extraction, list the important points as bullets.
For question answering, answer the student's question using the document.
For topic explanation, explain the requested topic using the document.

If the document does not contain enough information, say so.
"""

    encoded_file = base64.b64encode(file_bytes).decode("utf-8")

    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)

        if mime_type == "application/pdf":
            file_input = {
                "type": "document",
                "data": encoded_file,
                "mime_type": mime_type,
            }
        else:
            file_input = {
                "type": "image",
                "data": encoded_file,
                "mime_type": mime_type,
            }

        result = client.interactions.create(
            model="gemini-3.8-flash",
            input=[
                {
                    "type": "text",
                    "text": prompt,
                },
                file_input,
            ],
        )

        answer = result.output_text

        if not answer or not answer.strip():
            raise RuntimeError("Gemini returned an empty answer.")

        return answer.strip()

    except Exception as error:
        raise RuntimeError(
            f"File analysis failed: {error}"
        ) from error

# --------------------------------------------------
# 7. Session state and conversation helpers
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "file_answer" not in st.session_state:
    st.session_state.file_answer = None


def load_conversations():
    user = st.session_state.get("user")

    if not user:
        return []

    try:
        result = (
            supabase.table("conversations")
            .select("*")
            .eq("user_id", user.id)
            .order("updated_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception as error:
        st.error(f"Could not load saved conversations: {error}")
        return []
        
def save_conversation(title, messages):
    """Save a conversation for the currently logged-in student."""

    user = st.session_state.get("user")
    access_token = st.session_state.get("access_token")

    if not user or not access_token:
        st.error("Please log in before saving conversations.")
        return False

    try:
        supabase.postgrest.auth(access_token)

        result = supabase.table("conversations").insert({
            "user_id": user.id,
            "title": title.strip() or "New conversation",
            "messages": messages,
        }).execute()

        if result.data:
            st.success("Conversation saved successfully!")
            return True

        st.error("The conversation could not be saved.")
        return False

    except Exception as error:
        st.error(f"Failed to save conversation: {error}")
        return False
# --------------------------------------------------
# --------------------------------------------------
# Sidebar: Saved Conversations
# --------------------------------------------------

with st.sidebar:
    st.header("💬 Chat History")

    conversation_name = st.text_input(
        "Conversation name",
        placeholder="Example: Python Study Notes",
        key="conversation_name",
    )

    if st.button(
        "💾 Save Current Conversation",
        use_container_width=True,
    ):
        if not st.session_state.messages:
            st.warning("There is no conversation to save.")
        else:
            name = conversation_name.strip() or "New conversation"

            save_conversation(
                name,
                st.session_state.messages,
            )
            st.rerun()

    st.divider()
    st.subheader("📚 Saved Conversations")

    saved_items = load_conversations()

    if saved_items:
        selected_index = st.selectbox(
            "Choose a conversation",
            options=list(range(len(saved_items))),
            format_func=lambda i: (
                f"{saved_items[i]['title']} "
                f"({saved_items[i].get('created_at', '')[:10]})"
            ),
            key="selected_saved_conversation",
        )

        selected_conversation = saved_items[selected_index]

        if st.button(
            "📂 Open Conversation",
            use_container_width=True,
        ):
            import copy

            st.session_state.messages = copy.deepcopy(
                selected_conversation.get("messages", [])
            )
            st.rerun()

        if st.button(
            "🗑️ Delete Saved Conversation",
            use_container_width=True,
        ):
            user = st.session_state.get("user")

            try:
                (
                    supabase.table("conversations")
                    .delete()
                    .eq("id", selected_conversation["id"])
                    .eq("user_id", user.id)
                    .execute()
                )
                st.success("Conversation deleted.")
                st.rerun()

            except Exception as error:
                st.error(
                    f"Could not delete conversation: {error}"
                )

        st.download_button(
            "⬇️ Download Saved Conversations",
            data=json.dumps(
                saved_items,
                ensure_ascii=False,
                indent=2,
            ),
            file_name="saved_conversations.json",
            mime="application/json",
            use_container_width=True,
        )

    else:
        st.caption("Your saved conversations will appear here.")
# --------------------------------------------------
# 9. Main page
# --------------------------------------------------

# --------------------------------------------------
# Dashboard Feature Cards
# --------------------------------------------------

st.markdown(
    """
    <style>
    .feature-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 22px 18px;
        min-height: 150px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 22px rgba(15, 23, 42, 0.09);
    }

    .feature-icon {
        font-size: 30px;
        margin-bottom: 12px;
    }

    .feature-title {
        font-size: 17px;
        font-weight: 700;
        color: #163b70;
        margin-bottom: 8px;
    }

    .feature-description {
        color: #64748b;
        font-size: 14px;
        line-height: 1.6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
if "selected_feature" not in st.session_state:
    st.session_state.selected_feature = "chat"

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 💬 AI Study Chat")
    st.write(
        "Ask questions and understand difficult concepts "
        "with AI-powered explanations."
    )
    if st.button("Open AI Chat", key="open_ai_chat", use_container_width=True):
        st.session_state["selected_feature"] = "chat"
        st.rerun()

with col2:
    st.markdown("### 🎙️ Voice Assistant")
    st.write(
        "Speak your questions and listen to AI responses."
    )
    if st.button("Open Voice Assistant", key="open_voice", use_container_width=True):
        st.session_state["selected_feature"] = "voice"
        st.rerun()

with col3:
    st.markdown("### 📚 Study Materials")
    st.write(
        "Get help understanding uploaded PDFs and images."
    )
    if st.button("Open Study Materials", key="open_materials", use_container_width=True):
        st.session_state["selected_feature"] = "materials"
        st.rerun()
                
       
    

st.write("")

language = st.selectbox(
    "Choose your answer language",
    [
        "English",
        "Telugu",
        "Tamil",
        "Hindi",
        "Kannada",
        "Malayalam",
    ],
)

auto_speak = st.checkbox(
    "🔊 Automatically speak AI answers",
    value=False,
)

if st.button("🧪 Test Gnani Voice"):
    try:
        with st.spinner("Testing Gnani voice..."):
            test_audio = generate_speech(
                "Hello, this is a short voice test.",
                "English",
            )
        st.success("Voice generation successful!")
        st.audio(test_audio, format="audio/wav")
    except Exception as error:
        st.error(f"Gnani test failed: {error}")

if not GEMINI_API_KEY:
    st.warning(
        "Gemini API key not found. Check GEMINI_API_KEY "
        "in your local .env file."
    )

# --------------------------------------------------

# 10. Student chat with voice input
# --------------------------------------------------

selected_feature = st.session_state.get("selected_feature", "chat")

if selected_feature in ["chat", "voice"]:

    if selected_feature == "chat":
        st.markdown(
            """
            <div style="
                margin-top: 30px;
                margin-bottom: 18px;
                padding-bottom: 12px;
                border-bottom: 2px solid #dbeafe;
            ">
                <h2 style="
                    color: #163b70;
                    margin: 0;
                    font-size: 26px;
                ">
                    💬 Ask Multilingual AI
                </h2>
                <p style="
                    color: #64748b;
                    margin: 6px 0 0 0;
                    font-size: 15px;
                ">
                    Your personal AI tutor is ready to help you learn.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.header("🎙️ Voice Assistant")
        st.write("Speak your question and receive an AI answer.")

    if selected_feature == "chat":
        for index, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                if message["role"] == "assistant":
                    if st.button(
                        "🔊 Listen to answer",
                        key=f"listen_{index}",
                    ):
                        try:
                            with st.spinner("Generating voice..."):
                                audio_bytes = generate_speech(
                                    message["content"],
                                    language,
                                )
                            st.audio(audio_bytes, format="audio/wav")
                        except Exception as error:
                            st.error(f"Voice generation failed: {error}")

    speech_languages = {
        "English": "en",
        "Telugu": "te",
        "Tamil": "ta",
        "Hindi": "hi",
        "Kannada": "kn",
        "Malayalam": "ml",
    }

    if selected_feature == "voice":
        st.subheader("🎤 Ask by voice")

    voice_question = speech_to_text(
        language=speech_languages.get(language, "en"),
        start_prompt="🎤 Start speaking",
        stop_prompt="⏹️ Stop recording",
        just_once=True,
        use_container_width=True,
        key="student_voice_input",
    )

    if voice_question:
        st.session_state["question_from_voice"] = voice_question

    with st.form("student_question_form", clear_on_submit=True):
        question = st.text_area(
            "Type your question here",
            value=st.session_state.get("question_from_voice", ""),
            placeholder="Type your question or use voice input above.",
            height=100,
        )
        submitted = st.form_submit_button("Send question")

    if submitted:
        st.session_state.pop("question_from_voice", None)

        if not question.strip():
            st.warning("Please type or speak a question first.")
        else:
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": question.strip(),
                }
            )

            
            try:
                with st.spinner("Multilingual AI is thinking..."):
                    answer = generate_ai_answer(question.strip(), language)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                if auto_speak:
                    try:
                        with st.spinner("Generating voice..."):
                            audio_bytes = generate_speech(answer, language)
                        st.audio(audio_bytes, format="audio/wav")
                    except Exception as speech_error:
                        st.warning(
                            f"Voice generation failed: {speech_error}"
                        )

                st.rerun()

            except Exception:
                st.error(
                    "Sorry, we couldn't generate an answer right now. "
                    "Please try again in a moment."
                )

        if st.button("Clear chat"):
            st.session_state.messages = []
            st.session_state.pop("question_from_voice", None)
            st.session_state.file_answer = None
            st.rerun()

# --------------------------------------------------
# 11. Photo / PDF tutor
# --------------------------------------------------

# 11. Photo / PDF tutor

if st.session_state.get("selected_feature", "chat") == "materials":

    st.divider()
    st.header("📷 Photo Question Solver & PDF Tutor")

    st.write(
        "Upload a question paper, textbook page, diagram, "
        "or PDF and ask for an explanation."
    )

    uploaded_file = st.file_uploader(
        "Upload a photo or PDF",
        type=["jpg", "jpeg", "png", "webp", "pdf"],
        key="study_file",
    )

    task = st.selectbox(
        "What would you like to do?",
        [
            "Summarize PDF",
            "Extract key points",
            "Answer a question",
            "Explain a topic",
        ],
    )

    file_question = st.text_area(
        "Enter your question or topic (optional for summaries)",
        key="study_question",
    )

    if st.button("Analyze Photo / PDF"):
        if uploaded_file is None:
            st.warning("Please upload a PDF or image first.")
        elif (
            task in ["Answer a question", "Explain a topic"]
            and not file_question.strip()
        ):
            st.warning("Please enter a question or topic.")
        else:
            try:
                with st.spinner("Analyzing your file..."):
                    answer = generate_file_answer(
                        uploaded_file,
                        file_question.strip(),
                        language,
                        task,
                    )
                st.session_state.file_answer = answer
            except Exception as error:
                st.error(
    "Sorry, we couldn't analyze the file right now. "
    "Please try again with a different file."
)

    if st.session_state.file_answer:
        st.subheader("📝 Explanation")
        st.write(st.session_state.file_answer)
# --------------------------------------------------
# 12. Footer
# --------------------------------------------------

st.divider()
st.caption(
    "Multilingual AI Student Assistant | "
    "Use AI explanations as a study aid and verify important information."
)
# --------------------------------------------------
# Professional Dashboard Footer
# --------------------------------------------------

st.markdown(
    """
    <div style="
        margin-top: 45px;
        padding: 20px;
        text-align: center;
        border-top: 1px solid #e2e8f0;
        color: #64748b;
        font-size: 13px;
    ">
        <p style="margin: 0 0 6px 0; font-weight: 600;">
            🎓 Multilingual AI Student Assistant
        </p>
        <p style="margin: 0;">
            Learn smarter. Learn in your language.
        </p>
        <p style="margin: 8px 0 0 0;">
            Powered by AI · Built for students
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("🔒 Privacy Notice"):
    st.markdown("""
    ### Your Privacy Matters

    - **Account information:** Your account may be used to identify you
      when you sign in.
    - **Chat history:** Conversations may be saved to your account
      so you can access them later.
    - **AI processing:** Questions and uploaded content may be sent to
      external AI services to generate answers.
    - **Uploaded files:** Avoid uploading confidential documents,
      passwords, financial details, or sensitive personal information.
    - **Voice features:** Voice recordings or transcribed text may be
      processed by the services used to provide voice assistance.
    - **Data protection:** Access to saved conversations is restricted
      through database security policies.

    Please avoid sharing sensitive personal information. If you have
    questions about your data, contact the app administrator.
    """)
