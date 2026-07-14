"""
chatbot.py - Google Gemini-powered chatbot logic for Smart Campus AI.

Provides the ``get_ai_response`` function and a system prompt tailored
for a campus assistant. Chat messages are persisted to JSON.
"""

from __future__ import annotations

import streamlit as st

from config import GEMINI_API_KEY, GEMINI_MODEL
from database import save_chat_message, get_chat_history


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are Smart Campus AI — an intelligent assistant for university
students. Your role is to:

1. Answer academic questions across all engineering subjects.
2. Help students plan their study schedules and revision timetables.
3. Summarise assignment topics and suggest approaches.
4. Answer campus FAQs (library hours, exam schedules, placement info, etc.).
5. Provide motivational support and exam preparation tips.
6. Assist with coding questions, algorithm explanations, and project ideas.

Tone: Friendly, concise, and encouraging. Always support students positively.
Format: Use markdown for clarity — bullet points, headings, and code blocks where helpful.
If you do not know something specific to the campus, say so and suggest the relevant office.
"""


# ---------------------------------------------------------------------------
# AI response
# ---------------------------------------------------------------------------


def get_ai_response(user_message: str, user_email: str = "") -> str:
    """
    Send *user_message* to the Google Gemini API and return the response text.

    Persists both the question and answer to the chat history database.

    Parameters
    ----------
    user_message : str
        The student's query.
    user_email : str
        Used to key the chat history. Pass empty string for anonymous.

    Returns
    -------
    str
        AI-generated response or an error message.
    """
    if not GEMINI_API_KEY:
        return (
            "⚠️ **Gemini API key is not configured.**\n\n"
            "Please add `GEMINI_API_KEY=your_key` to your `.env` file "
            "and restart the application."
        )

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)

        # Build conversation history for context using roles: 'user' and 'model'
        contents = []

        if user_email:
            history = get_chat_history(user_email, limit=10)
            for entry in history[-5:]:  # last 5 exchanges for context
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=entry.get("question", ""))]
                    )
                )
                contents.append(
                    types.Content(
                        role="model",
                        parts=[types.Part.from_text(text=entry.get("answer", ""))]
                    )
                )

        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)]
            )
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=1024,
            ),
        )

        answer: str = response.text or ""

        if user_email:
            save_chat_message(user_email, user_message, answer)

        return answer

    except ImportError:
        return (
            "❌ The `google-genai` package is not installed.\n\n"
            "Run: `pip install google-genai`"
        )
    except Exception as exc:  # noqa: BLE001
        error_msg = str(exc)
        if "authentication" in error_msg.lower() or "api key" in error_msg.lower() or "api_key" in error_msg.lower() or "api-key" in error_msg.lower():
            return (
                "🔑 **Invalid API key.** Please check your `GEMINI_API_KEY` in the `.env` file."
            )
        elif "rate limit" in error_msg.lower() or "429" in error_msg.lower():
            return (
                "⏳ **Rate limit reached.** Please wait a moment and try again."
            )
        elif "model" in error_msg.lower() or "not found" in error_msg.lower():
            return (
                f"🤖 **Model error.** The model `{GEMINI_MODEL}` may not be available "
                "on your account. Try changing `GEMINI_MODEL` in your `.env` file."
            )
        else:
            return f"❌ **An error occurred:** {error_msg}"


def build_chat_interface(user_email: str) -> None:
    """
    Render the full chat UI inside the calling page.

    Parameters
    ----------
    user_email : str
        Email of the logged-in user (used to scope chat history).
    """
    # Initialise session messages from DB on first load
    if "chat_messages" not in st.session_state or not st.session_state["chat_messages"]:
        db_history = get_chat_history(user_email, limit=20)
        st.session_state["chat_messages"] = [
            {"role": "assistant", "content": (
                "👋 Hello! I'm **Smart Campus AI**, your personal academic assistant.\n\n"
                "Ask me anything — study plans, coding help, campus FAQs, assignment tips, "
                "or just a motivational boost! 🚀"
            )},
        ]
        for entry in db_history:
            st.session_state["chat_messages"].append(
                {"role": "user", "content": entry["question"]}
            )
            st.session_state["chat_messages"].append(
                {"role": "assistant", "content": entry["answer"]}
            )

    # Render chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
                st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("Ask me anything about your studies, campus, or assignments…"):
        # Add user message
        st.session_state["chat_messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Get and display AI response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking…"):
                response = get_ai_response(prompt, user_email)
            st.markdown(response)

        st.session_state["chat_messages"].append({"role": "assistant", "content": response})
        st.rerun()
