from .simple_recipe_search import search_recipe
from .rag_pipeline import query_similar


def generate_chef_response(ingredients: list, prefs: str = ""):

    # =========================
    # RAG (optional recommendations)
    # =========================
    try:
        similar_recipes = query_similar(ingredients, top_k=2)
    except Exception:
        similar_recipes = []

    # =========================
    # SEARCH RECIPE (LOCAL DB)
    # =========================
    recipe = search_recipe(ingredients)

    # =========================
    # FALLBACK IF NOTHING FOUND
    # =========================
    if not recipe:

        body = """
        <p><b>No matching recipe found.</b></p>
        <p>Try adding more or different ingredients.</p>
        """

        return (
            "Chef's Surprise",
            body,
            similar_recipes
        )

    # =========================
    # INGREDIENTS (HTML LIST)
    # =========================
    ingredients_html = ""

    for ing in recipe.get("ingredients", []):
        ingredients_html += f"<li>{ing}</li>"

    # =========================
    # INSTRUCTIONS (CLEAN STEPS)
    # =========================
    instructions_raw = recipe.get("instructions", "")

    steps = [
        step.strip()
        for step in instructions_raw.split(".")
        if step.strip()
    ]

    steps_html = ""

    for i, step in enumerate(steps, start=1):
        steps_html += f"""
        <div class="step">
            <b>Step {i}:</b> {step}.
        </div>
        """

    # =========================
    # FINAL OUTPUT (ONLY CONTENT)
    # =========================
    body_html = f"""

    <h3>🥘 Ingredients</h3>
    <ul>
        {ingredients_html}
    </ul>

    <h3>👨‍🍳 Instructions</h3>
    {steps_html}

    """

    return (
        recipe.get("title", "Chef Recipe"),
        body_html,
        similar_recipes
    )
