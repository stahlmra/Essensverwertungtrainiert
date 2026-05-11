import json

RECIPE_FILE = "seed_data/indian_recipes.jsonl"


def search_recipe(user_ingredients):
    matches = []

    with open(RECIPE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            recipe = json.loads(line)

            ingredients = recipe.get("ingredients", [])

            # Zutaten vergleichen
            score = sum(
                1 for ing in user_ingredients
                if ing.lower() in [i.lower() for i in ingredients]
            )

            if score > 0:
                matches.append((score, recipe))

    # beste Treffer zuerst
    matches.sort(reverse=True, key=lambda x: x[0])

    if matches:
        return matches[0][1]

    return None
