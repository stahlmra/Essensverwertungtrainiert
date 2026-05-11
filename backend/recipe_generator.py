from .simple_recipe_search import search_recipe
import re
from .rag_pipeline import query_similar
from .llm import generate_text

PROMPT_TEMPLATE = """
You are a professional Michelin-star chef. 
I have the following ingredients: {ingredients}.
Dietary Preferences: {prefs}.

Here is some context from my personal cookbook (use if relevant):
{context}

TASK:
Create ONE single, highly detailed recipe.
Do NOT use bold asterisks (**) for the Title or Labels.
Follow this format EXACTLY:

Title: [Name of the Dish]
Description: [A short, mouth-watering summary]
Time: [Prep & Cook Time] | Servings: [Number]

Ingredients
- [List items]

Instructions
1. [Step 1]
2. [Step 2]

Chef's Tip: [A professional secret tip]
"""


def clean_text(text):
    text = text.replace("**Title:**", "Title:").replace("**Description:**", "Description:")
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    return text


def generate_chef_response(ingredients: list, prefs: str = ""):

    # 1. RAG Kontext
    similar_recipes = query_similar(ingredients, top_k=2)

    context_str = ""
    for r in similar_recipes:
        context_str += f"- {r['title']} (Ingredients: {r['ingredients']})\n"

    # 2. Prompt bauen (für später KI optional)
    prompt = PROMPT_TEMPLATE.format(
        ingredients=", ".join(ingredients),
        prefs=prefs if prefs else "None",
        context=context_str if context_str else "No prior recipes found."
    )

    # 3. LOCAL RECIPE SEARCH (wichtig!)
    recipe = search_recipe(ingredients)

    # 4. Ergebnis bestimmen
    if recipe:
        raw_text = f"""
Title: {recipe.get('title', 'Rezept')}

Ingredients:
{", ".join(recipe.get('ingredients', []))}

Instructions:
{recipe.get('instructions', 'Keine Anleitung gefunden.')}
"""
    else:
        # fallback (optional KI später)
        raw_text = "❌ Kein passendes Rezept gefunden."

    # 5. Parsing
    lines = raw_text.strip().split('\n')

    title = "Chef's Special Creation"
    body_lines = []
    title_found = False

    for line in lines:
        line = clean_text(line.strip())

        if not line:
            continue

        if not title_found and line.startswith("Title:"):
            title = line.replace("Title:", "").strip()
            title_found = True

        elif line.startswith("Ingredients"):
            body_lines.append("<h3>Ingredients</h3>")

        elif line.startswith("Instructions"):
            body_lines.append("<h3>Instructions</h3>")

        elif line.startswith("- "):
            body_lines.append(f"<li>{line[2:]}</li>")

        elif re.match(r'^\d+\.', line):
            body_lines.append(f"<p class='step'>{line}</p>")

        else:
            body_lines.append(f"<p>{line}</p>")

    clean_body = "\n".join(body_lines)

    return title, clean_body, similar_recipes
