from .simple_recipe_search import search_recipe
import re
from .rag_pipeline import query_similar
from .llm import generate_text

# Updated Prompt to be cleaner
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

### Ingredients
- [List items]

### Instructions
1. [Step 1]
2. [Step 2]
...

Chef's Tip: [A professional secret tip]
"""

def clean_text(text):
    """
    Cleans up Markdown artifacts to ensure professional HTML rendering.
    """
    # 1. Remove asterisks from Title/Headers if LLM ignores instructions
    text = text.replace("**Title:**", "Title:").replace("**Description:**", "Description:")
    
    # 2. Convert remaining Markdown bold (**text**) to HTML (<b>text</b>)
    # This prevents raw asterisks from showing up in the UI
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    return text

def generate_chef_response(ingredients: list, prefs: str = ""):
    # 1. RAG Retrieval
    similar_recipes = query_similar(ingredients, top_k=2)
    
    context_str = ""
    for r in similar_recipes:
        context_str += f"- {r['title']} (Ingredients: {r['ingredients']})\n"

    # 2. Build Prompt
    prompt = PROMPT_TEMPLATE.format(
        ingredients=", ".join(ingredients),
        prefs=prefs if prefs else "None",
        context=context_str if context_str else "No prior recipes found."
    )

    recipe = search_recipe(ingredients_clean)

if recipe:
    raw_text = f"""
{recipe.get('title', 'Rezept')}

Ingredients:
{", ".join(recipe.get('ingredients', []))}

Instructions:
{recipe.get('instructions', 'Keine Anleitung gefunden.')}
"""
else:
    raw_text = "❌ Kein passendes Rezept gefunden."

    # 4. Parse & Clean
    lines = raw_text.strip().split('\n')
    title = "Chef's Special Creation"
    body_lines = []
    
    title_found = False

    for line in lines:
        line = clean_text(line.strip())
        
        # Extract Title
        if not title_found and (line.startswith("Title:") or line.startswith("##")):
            title = line.replace("Title:", "").replace("##", "").strip()
            title_found = True
        # Format Description line specifically
        elif line.startswith("Description:"):
            # wrap 'Description:' in a span for CSS styling
            content = line.replace("Description:", "").strip()
            body_lines.append(f"<p class='recipe-desc'><span class='label'>Description:</span> {content}</p>")
        # Format Time/Servings line
        elif line.startswith("Time:"):
            body_lines.append(f"<p class='recipe-meta'>{line}</p>")
        # Keep Ingredients/Instructions headers clean
        elif "Ingredients" in line and "###" in line:
            body_lines.append(f"<h3>Ingredients</h3>")
        elif "Instructions" in line and "###" in line:
            body_lines.append(f"<h3>Instructions</h3>")
        # Format Lists (Simple bullet handling)
        elif line.startswith("- "):
            body_lines.append(f"<li>{line[2:]}</li>")
        elif re.match(r'^\d+\.', line):
            # Wrap numbered steps
            body_lines.append(f"<p class='step'>{line}</p>")
        else:
            if line:
                body_lines.append(f"<p>{line}</p>")

    # Join body lines
    clean_body = "\n".join(body_lines)

    return title, clean_body, similar_recipes
