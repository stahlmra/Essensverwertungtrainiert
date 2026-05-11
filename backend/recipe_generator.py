from .simple_recipe_search import search_recipe
from .rag_pipeline import query_similar


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
    # SEARCH RECIPE
    # =========================
    recipe = search_recipe(ingredients)

    if not recipe:
        return (
            "No Recipe Found",
            "<p>No recipe found for these ingredients.</p>",
            similar_recipes
        )

    # =========================
    # INGREDIENTS
    # =========================
    ingredients_html = "".join(
        f"<li>{i}</li>" for i in recipe.get("ingredients", [])
    )

    # =========================
    # INSTRUCTIONS
    # =========================
    instructions = recipe.get("instructions", "")

    steps = [
        s.strip()
        for s in instructions.split(".")
        if s.strip()
    ]

    steps_html = "".join(
        f"<div class='step'><b>Step {idx+1}:</b> {step}.</div>"
        for idx, step in enumerate(steps)
    )

    # =========================
    # RETURN ONLY CONTENT (NO CARD!)
    # =========================
    body_html = f"""
    <h3>🥘 Ingredients</h3>
    <ul>{ingredients_html}</ul>

    <h3>👨‍🍳 Instructions</h3>
    {steps_html}
    """

    return (
        recipe.get("title", "Chef Recipe"),
        body_html,
        similar_recipes
    )
