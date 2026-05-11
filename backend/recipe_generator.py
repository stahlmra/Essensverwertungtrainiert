# =========================
# backend/recipe_generator.py
# =========================

from .simple_recipe_search import search_recipe
from .rag_pipeline import query_similar
import re

# =========================
# CLEAN TEXT
# =========================
def clean_text(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    return text


# =========================
# MAIN FUNCTION
# =========================
def generate_chef_response(ingredients: list, prefs: str = ""):

    # =========================
    # RAG SEARCH
    # =========================
    try:
        similar_recipes = query_similar(ingredients, top_k=2)
    except Exception:
        similar_recipes = []

    # =========================
    # LOCAL RECIPE SEARCH
    # =========================
    recipe = search_recipe(ingredients)

    # =========================
    # NO RECIPE FOUND
    # =========================
    if not recipe:

        empty_html = """
        <h3>No Recipe Found</h3>

        <p>
        We could not find a matching recipe for your ingredients.
        Try adding more ingredients.
        </p>
        """

        return (
            "No Recipe Found",
            empty_html,
            similar_recipes
        )

    # =========================
    # FORMAT INGREDIENTS
    # =========================
    ingredients_html = ""

    for ing in recipe.get("ingredients", []):
        ingredients_html += f"<li>{clean_text(ing)}</li>"

    # =========================
    # FORMAT INSTRUCTIONS
    # =========================
    instructions_raw = recipe.get(
        "instructions",
        "No instructions available."
    )

    instruction_parts = [
        x.strip()
        for x in instructions_raw.split(".")
        if x.strip()
    ]

    instructions_html = ""

    for step in instruction_parts:
        instructions_html += f"""
        <div class="step">
            • {clean_text(step)}.
        </div>
        """

    # =========================
    # FINAL HTML
    # =========================
    body_html = f"""

    <div class="recipe-section">

        <h3>🥘 Ingredients</h3>

        <ul>
            {ingredients_html}
        </ul>

        <h3>👨‍🍳 Instructions</h3>

        {instructions_html}

    </div>
    """

    # =========================
    # RETURN
    # =========================
    return (
        recipe.get("title", "Chef Recipe"),
        body_html,
        similar_recipes
    )
