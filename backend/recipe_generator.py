from .simple_recipe_search import search_recipe
from .rag_pipeline import query_similar


def generate_chef_response(ingredients: list, prefs: str = ""):

    # =========================
    # RAG
    # =========================
    try:
        similar_recipes = query_similar(ingredients, top_k=2)
    except Exception:
        similar_recipes = []

    # =========================
    # RECIPE FETCH
    # =========================
    recipe = search_recipe(ingredients)

    if not recipe:
        return (
            "No Recipe Found",
            {
                "ingredients": [],
                "instructions": []
            },
            similar_recipes
        )

    # =========================
    # CLEAN DATA OUTPUT (WICHTIG!)
    # =========================
    instructions_raw = recipe.get("instructions", "")

    instructions_list = [
        s.strip()
        for s in instructions_raw.split(".")
        if s.strip()
    ]

    return (
        recipe.get("title", "Chef Recipe"),
        {
            "ingredients": recipe.get("ingredients", []),
            "instructions": instructions_list
        },
        similar_recipes
    )
