import streamlit as st
from PIL import Image
import io
import os

from backend.img_ingred_detection import extract_ingredients
from backend.recipe_generator import generate_chef_response

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Chef's Table AI",
    page_icon="🍽️",
    layout="centered"
)

# =========================
# DATABASE CHECK
# =========================
if not os.path.exists("./chroma_db"):
    try:
        if os.path.exists("scripts/seed_chroma.py"):
            from scripts.seed_chroma import seed
            seed()
    except Exception:
        pass

# =========================
# SESSION STATE
# =========================
if "ingredients_list" not in st.session_state:
    st.session_state.ingredients_list = ""
if "recipe_title" not in st.session_state:
    st.session_state.recipe_title = None
if "recipe_body" not in st.session_state:
    st.session_state.recipe_body = None
if "rag_recommendations" not in st.session_state:
    st.session_state.rag_recommendations = []

# =========================
# 🍷 FINE DINING CSS
# =========================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;600&display=swap');

.stApp {
    background-color: #f7f3ee;
    font-family: 'Inter', sans-serif;
}

/* HEADER */
h1 {
    text-align: center;
    font-family: 'Playfair Display', serif;
    color: #2b1d14;
    font-size: 44px;
}

/* SUBTITLE */
.subtitle {
    text-align: center;
    color: #6b5b4d;
    margin-bottom: 30px;
}

/* MAIN CARD */
.recipe-card {
    background: white;
    border-radius: 20px;
    padding: 35px;
    margin-top: 25px;
    box-shadow: 0 15px 40px rgba(0,0,0,0.08);
    border: 1px solid #eee;
}

/* TITLE */
.recipe-title {
    font-family: 'Playfair Display', serif;
    font-size: 34px;
    color: #1f1510;
    border-bottom: 3px solid #c9a66b;
    display: inline-block;
    padding-bottom: 8px;
    margin-bottom: 10px;
}

/* BADGE */
.badge {
    float: right;
    background: #1f1510;
    color: white;
    padding: 6px 14px;
    border-radius: 50px;
    font-size: 11px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* SECTION HEADERS */
h3 {
    font-family: 'Playfair Display', serif;
    margin-top: 25px;
    color: #2b1d14;
}

/* STEPS */
.step {
    margin-left: 10px;
    padding: 4px 0;
    line-height: 1.6;
}

/* RAG CARDS */
.rag-card {
    background: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #eee;
    box-shadow: 0 3px 10px rgba(0,0,0,0.05);
}

/* INPUT */
.stTextInput input {
    border-radius: 12px;
    padding: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("# 🍽️ Chef's Table AI")
st.markdown("<div class='subtitle'>Fine Dining Experience powered by AI</div>", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("Preferences")
    prefs = st.text_input("Dietary Preferences", placeholder="Vegetarian, Keto, etc.")
    st.info("📸 Upload image or type ingredients manually")

# =========================
# INPUT TABS
# =========================
tabs = st.tabs(["📸 Image", "✍️ Manual"])

# TAB IMAGE
with tabs[0]:
    uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])

    if uploaded:
        st.image(uploaded, use_container_width=True)

        if st.button("Detect Ingredients"):
            uploaded.seek(0)
            detected = extract_ingredients(uploaded.read())

            if detected:
                st.session_state.ingredients_list = ", ".join(detected)
            else:
                st.session_state.ingredients_list = ""

            st.rerun()

# TAB MANUAL
with tabs[1]:
    st.write("Enter ingredients manually if needed.")

# =========================
# INGREDIENT EDITOR
# =========================
st.divider()
st.subheader("🥕 Ingredients")

final = st.text_area(
    "Edit ingredients:",
    value=st.session_state.ingredients_list,
    placeholder="tomato, onion, garlic..."
)

st.session_state.ingredients_list = final

# =========================
# COOK BUTTON
# =========================
if st.button("🍷 Create Dish", type="primary"):

    ingredients = [x.strip() for x in final.split(",") if x.strip()]

    if not ingredients:
        st.error("Please enter ingredients")
    else:
        title, body, rag = generate_chef_response(ingredients, prefs)

        st.session_state.recipe_title = title
        st.session_state.recipe_body = body
        st.session_state.rag_recommendations = rag

        st.rerun()

# =========================
# OUTPUT
# =========================
if st.session_state.recipe_body:

    st.divider()

    st.markdown(f"""
    <div class="recipe-card">
        <span class="badge">Chef AI</span>
        <div class="recipe-title">{st.session_state.recipe_title}</div>
        {st.session_state.recipe_body}
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # RAG SECTION
    # =========================
    if st.session_state.rag_recommendations:
        st.subheader("📚 Inspired Recipes")

        cols = st.columns(len(st.session_state.rag_recommendations))

        for i, r in enumerate(st.session_state.rag_recommendations):
            with cols[i]:
                st.markdown(f"""
                <div class="rag-card">
                    <b>{r['title']}</b><br>
                    <small>Match: {1 - r.get('score', 0):.2f}</small>
                </div>
                """, unsafe_allow_html=True)
