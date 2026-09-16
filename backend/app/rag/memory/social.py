import re


def social_reply(message: str) -> str | None:
    """Route only whole-message social turns; mixed questions still use RAG."""
    normalized = re.sub(r"[^\w\s]", " ", message.casefold())
    normalized = " ".join(normalized.split())
    if normalized in {"hi", "hello", "hey", "hi there", "hello there", "hey there",
                      "good morning", "good afternoon", "good evening"}:
        return "Hi! How can I help you with your documents?"
    if normalized in {"thanks", "thank you", "thanks a lot", "thank you very much"}:
        return "You're welcome!"
    if normalized in {"bye", "goodbye", "see you", "see you later"}:
        return "Goodbye! Feel free to come back with more questions."
    return None
