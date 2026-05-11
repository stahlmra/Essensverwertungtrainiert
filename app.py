import streamlit as st
import os

from backend.img_ingred_detection import extract_ingredients
from backend.recipe_generator import generate_chef_response


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Michelin Chef AI",
    page_icon="⭐",
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
# MICHELIN CSS
# =========================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Inter:wght@300;400;500&display=swap');

.stApp {
    background: linear-gradient(180deg, #0d0d0d 0%, #151515 100%);
    color: #f5f5f5;
}

.main-title {
    text-align: center;
    font-family: 'Cormorant Garamond', serif;
    font-size: 60px;
    color: #d4af37;
    margin-bottom: 0;
}

.subtitle {
    text-align: center;
    color: #d0d0d0;
    margin-bottom: 40px;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.recipe-card {
    background: linear-gradient(145deg, #181818, #111111);
    border: 1px solid rgba(212,175,55,0.25);
    border-radius: 24px;
    padding: 40px;
    margin-top: 30px;
}

.recipe-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 42px;
    color: #f8e7b0;
    margin-bottom: 20px;
    border-bottom: 2px solid #d4af37;
    display: inline-block;
    padding-bottom: 10px;
}

.badge {
    float: right;
    background: linear-gradient(90deg, #8b6b1f, #d4af37);
    color: black;
    padding: 8px 14px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 2px;
    text-transform: uppercase;
}

h3 {
    font-family: 'Cormorant Garamond', serif;
    color: #d4af37;
}

.step {
    margin-bottom: 12px;
    padding-left: 10px;
    border-left: 2px solid rgba(212,175,55,0.4);
}

.stButton > button {
    background: linear-gradient(90deg, #8b6b1f, #d4af37);
    color: black;
    border-radius: 12px;
    font-weight: bold;
}

.rag-card {
    background: #161616;
    border: 1px solid rgba(212,175,55,0.15);
    border-radius: 16px;
    padding: 15px;
}

</style>
""", unsafe_allow_html=True)


# =========================
# HEADER
# =========================
st.markdown("""
<div class="main-title">Michelin Chef AI</div>
<div class="subtitle">Luxury Fine Dining Experience</div>
""", unsafe_allow_html=True)


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("Preferences")
    prefs = st.text_input("Dietary Preferences", placeholder="Vegetarian, Keto...")

    st.info("📸 Upload image or type ingredients")


# =========================
# INPUT
# =========================
st.subheader("🥂 Ingredients")

final_ingredients = st.text_area(
    "Enter ingredients:",
    value=st.session_state.ingredients_list,
    placeholder="tomato, onion, garlic..."
)

st.session_state.ingredients_list = final_ingredients


# =========================
# GENERATE
# =========================
if st.button("⭐ Create Michelin Dish"):

    ingredients_clean = [
        x.strip()
        for x in final_ingredients.split(",")
        if x.strip()
    ]

    if not ingredients_clean:
        st.error("Please enter ingredients.")
    else:
        with st.spinner("👨‍🍳 Cooking your Michelin dish..."):

            title, body, rag = generate_chef_response(
                ingredients_clean,
                prefs
            )

            st.session_state.recipe_title = title
            st.session_state.recipe_body = body
            st.session_state.rag_recommendations = rag

        st.rerun()


# =========================
# OUTPUT
# =========================
if st.session_state.recipe_body:

    st.markdown(f"""
    <div class="recipe-card">

        <span class="badge">Michelin Inspired</span>

        <div class="recipe-title">
            {st.session_state.recipe_title}
        </div>

        {st.session_state.recipe_body}

    </div>
    """, unsafe_allow_html=True)


# =========================
# RAG SECTION
# =========================
if st.session_state.rag_recommendations:

    st.subheader("⭐ Chef Inspirations")

    cols = st.columns(len(st.session_state.rag_recommendations))

    for i, rec in enumerate(st.session_state.rag_recommendations):

        with cols[i]:

            score = abs(1 - rec.get("score", 0))

            st.markdown(f"""
            <div class="rag-card">
                <b style="color:#f8e7b0">{rec['title']}</b>
                <p style="color:#d4af37;">Match: {score:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
