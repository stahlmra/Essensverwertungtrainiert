import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_text(prompt: str, max_tokens: int = 800) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a Michelin-star chef that creates structured recipes."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(e)
        return "Fehler: KI konnte nicht geladen werden (API prüfen)"
