# 🎓 Gnani AI Multilingual Student Assistant

An AI-powered multilingual student assistant built using Python and Streamlit. It helps students with academic questions, AI concepts, study support and career guidance through text and voice interaction.

🌐 **Live Demo:** https://multilingual-ai-student-assistant-vdcadubd28bnnxfep9jqig.streamlit.app/

💻 **GitHub Repository:** https://github.com/koramutlacharansai7-crypto/multilingual-ai-student-assistant

## 📌 Project Overview

The Gnani AI Multilingual Student Assistant combines generative AI, speech recognition, text-to-speech and database integration to provide an accessible learning experience.

## ✨ Key Features

- AI-powered student chat using Google Gemini.
- Voice input using a microphone.
- Speech-to-text using Gnani AI.
- Multilingual interaction in English, Tamil, Telugu and Hindi.
- Text-to-speech using Gnani AI.
- Audio playback of AI-generated answers.
- Student login and authentication.
- Saved conversations using Supabase.
- Image and PDF question analysis.
- Cloud deployment using Streamlit Community Cloud.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Web interface |
| Google Gemini API | AI-generated responses |
| Gnani AI | Speech-to-text and text-to-speech |
| Supabase | Authentication and database |
| Requests | API communication |
| python-dotenv | Environment variable management |
| GitHub | Version control |

## 🏗️ Application Workflow

1. Student opens the application and signs in.
2. Student asks a question through text or voice.
3. Gnani AI converts voice into text.
4. Google Gemini processes the question.
5. The AI-generated answer is displayed.
6. Gnani AI converts the answer into speech.
7. Conversations can be saved and revisited through Supabase.

## ⚙️ Run the Project Locally

### Prerequisites
- Python
- Google Gemini API credentials
- Gnani AI API credentials
- Supabase project credentials

### 1. Clone the repository

```bash
git clone https://github.com/koramutlacharansai7-crypto/multilingual-ai-student-assistant.git
```

### 2. Open the project directory

```bash
cd multilingual-ai-student-assistant
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file and configure the environment variable names used in `app.py`.

Never upload API keys or passwords to GitHub.

### 5. Run the application

```bash
python -m streamlit run app.py
```

## ☁️ Deployment

The application is deployed using Streamlit Community Cloud.

**Live Application:**

https://multilingual-ai-student-assistant-vdcadubd28bnnxfep9jqig.streamlit.app/

## 🔐 Security and Privacy

- Do not upload `.env` files or API keys.
- Store deployment credentials using Streamlit Cloud secrets.
- Use appropriate Supabase Row Level Security policies.
- Never expose private credentials in public documentation.

## 🎯 Project Objectives

- Make AI-powered learning assistance accessible.
- Support multilingual text and voice interaction.
- Help students with academic and career-related questions.
- Explore generative AI, speech technologies and database integration.

## 🎓 Learning Outcomes

- Python application development.
- Generative AI integration.
- Speech recognition and speech synthesis.
- Streamlit application development.
- Database and authentication integration.
- Cloud deployment and GitHub version control.

## 📸 Application Screenshots

### Home Page
![Home Page](p1.png)

### AI Chat
![AI Chat](pai.png)

### Voice Assistant
![Voice Assistant](p%20voice%20.png)
