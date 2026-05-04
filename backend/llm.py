import logging

logger = logging.getLogger(__name__)

_llm_instance = None


def load_llm():
    """
    Disabled local LLM for deployment stability.
    """
    global _llm_instance
    return None


def generate_text(prompt: str, max_tokens: int = 1024) -> str:
    """
    Fallback response without local model.
    Keeps app functional on Streamlit Cloud.
    """

    logger.info("LLM is disabled - returning fallback response")

    return (
        "🍳 Rezept-Generator (Demo-Modus)\n\n"
        "Deine Eingabe:\n"
        f"{prompt}\n\n"
        "⚠️ Hinweis: Lokales KI-Modell ist deaktiviert, damit die App stabil läuft.\n"
        "👉 Nächster Schritt wäre: API-Integration (z. B. OpenAI oder HuggingFace Inference)"
    )
