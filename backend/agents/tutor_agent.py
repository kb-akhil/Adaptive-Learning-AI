# ============================================================
# agents/tutor_agent.py — AI Tutor using Cohere API
# ============================================================
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COHERE_API_KEY

_client = None

def _setup_client():
    global _client
    if _client is not None:
        return True
    try:
        import cohere
        _client = cohere.ClientV2(api_key=COHERE_API_KEY)
        print("[TutorAgent] Cohere client ready.")
        return True
    except Exception as e:
        print(f"[TutorAgent] Cohere setup failed: {e}")
        return False


SYSTEM_PROMPT = """You are AgenticLearn AI Tutor for Computer Networks students.

Rules:
- Keep answers SHORT and SIMPLE — max 150 words
- Use simple English a student can understand
- Use bullet points for lists, NOT long paragraphs
- Give 1 small real-world example where helpful
- Never repeat the question back
- Never write essay-style answers
- If asked how something works, give max 4–5 bullet points
- End with ONE short follow-up tip (1 line only)"""


def ask_tutor(question: str, context_topic: str = "", history: list = None) -> dict:
    if not question or not question.strip():
        return {"answer": "Please ask a question.", "source": "fallback", "related_topics": []}

    if not _setup_client():
        return _fallback(question, context_topic)

    # Build message history for context
    messages = []
    if history:
        for h in history[-6:]:  # last 3 exchanges (6 messages)
            messages.append({"role": h["role"], "content": h["text"]})

    topic_hint = f" (Topic: {context_topic})" if context_topic else ""
    messages.append({"role": "user", "content": f"{question}{topic_hint}"})

    try:
        response = _client.chat(
            model="command-r-plus-08-2024",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        )
        answer = response.message.content[0].text.strip()
        print(f"[TutorAgent] Response: {len(answer)} chars")
        return {
            "answer":         answer,
            "source":         "cohere",
            "related_topics": _extract_related(question, context_topic)
        }
    except Exception as e:
        print(f"[TutorAgent] Cohere error: {e}")
        return _fallback(question, context_topic)


def _extract_related(question: str, topic: str = "") -> list:
    words   = re.findall(r'\b[A-Z][a-zA-Z]{3,}\b', question)
    related = list(dict.fromkeys(words))[:3]
    if topic and topic not in related:
        related.insert(0, topic)
    return related[:3] or ["Related Concepts", "Practical Applications"]


def _fallback(question: str, topic: str = "") -> dict:
    return {
        "answer":         "The AI Tutor is currently unavailable. Please try again shortly.",
        "source":         "fallback",
        "related_topics": _extract_related(question, topic)
    }