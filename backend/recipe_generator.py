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

        body = """
        <div class='recipe-text'>
            <p>No matching recipe found.</p>
            <p>Try adding more ingredients.</p>
        </div>
        """

        return (
            "No Recipe Found",
            body,
            similar_recipes
        )

    # =========================
    # INGREDIENTS HTML
    # =========================
    ingredients_html = ""

    for ing in recipe.get("ingredients", []):
        ingredients_html += f"<li>{clean_text(ing)}</li>"

    # =========================
    # INSTRUCTIONS HTML
    # =========================
    instructions_raw = recipe.get(
        "instructions",
        "No instructions available."
    )

    steps = [
        x.strip()
        for x in instructions_raw.split(".")
        if x.strip()
    ]

    instructions_html = ""

    for i, step in enumerate(steps, start=1):

        instructions_html += f"""
        <div class="step">
            <b>Step {i}:</b> {clean_text(step)}.
        </div>
        """

    # =========================
    # FINAL CLEAN HTML
    # =========================
    body = f"""
    <div class="recipe-content">

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
        body,
        similar_recipes
    )
