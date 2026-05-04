import os
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")


def generate_text(prompt: str, max_tokens: int = 800) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        logger.error(e)
        return "❌ Fehler: Gemini API konnte nicht geladen werden"
