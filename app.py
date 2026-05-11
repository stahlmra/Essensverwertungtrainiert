# =========================
# app.py
# =========================

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
    background: linear-gradient(
        180deg,
        #0d0d0d 0%,
        #151515 100%
    );
    color: #f5f5f5;
}

.main-title {
    text-align: center;
    font-family: 'Cormorant Garamond', serif;
    font-size: 64px;
    color: #d4af37;
    margin-bottom: 0;
}

.subtitle {
    text-align: center;
    color: #d0d0d0;
    margin-bottom: 40px;
    letter-spacing: 2px;
}

.recipe-card {
    background: linear-gradient(
        145deg,
        #181818,
        #111111
    );

    border: 1px solid rgba(212,175,55,0.25);

    border-radius: 24px;

    padding: 40px;

    margin-top: 30px;

    box-shadow:
        0 10px 30px rgba(0,0,0,0.45),
        0 0 25px rgba(212,175,55,0.08);
}

.recipe-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 42px;
    color: #f8e7b0;
    margin-bottom: 20px;
    border-bottom: 2px solid #d4af37;
    padding-bottom: 10px;
    display: inline-block;
}

.badge {
    float: right;

    background: linear-gradient(
        90deg,
        #8b6b1f,
        #d4af37
    );

    color: black;

    font-weight: bold;

    padding: 8px 16px;

    border-radius: 999px;

    font-size: 11px;

    letter-spacing: 2px;
}

h3 {
    font-family: 'Cormorant Garamond', serif;
    color: #d4af37;
    margin-top: 28px;
}

p, li {
    color: #e5e5e5;
    line-height: 1.8;
    font-size: 16px;
}

.step {
    margin-bottom: 12px;
    padding-left: 10px;
    border-left: 2px solid rgba(212,175,55,0.4);
}

.stButton > button {
    background: linear-gradient(
        90deg,
        #8b6b1f,
        #d4af37
    );

    color: black;

    border: none;

    border-radius: 14px;

    padding: 0.7rem 1.4rem;

    font-weight: bold;
}

.rag-card {
    background: #161616;

    border: 1px solid rgba(212,175,55,0.15);

    border-radius: 18px;

    padding: 20px;

    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("""
<div class="main-title">Michelin Chef AI</div>
<div class="subtitle">
Luxury Fine Dining Experience
</div>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.header("Chef Preferences")

    prefs = st.text_input(
        "Dietary Preferences",
        placeholder="Vegetarian, Vegan, Keto..."
    )

# =========================
# INPUT
# =========================
st.subheader("🥂 Ingredients")

final_ingredients = st.text_area(
    "Ingredients",
    value=st.session_state.ingredients_list,
    placeholder="truffle, pasta, parmesan..."
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

        with st.spinner("👨‍🍳 Michelin chef is preparing your dish..."):

            title, body, rag_recs = generate_chef_response(
                ingredients_clean,
                prefs
            )

            st.session_state.recipe_title = title
            st.session_state.recipe_body = body
            st.session_state.rag_recommendations = rag_recs

        st.rerun()

# =========================
# OUTPUT
# =========================
if st.session_state.recipe_body:

    st.markdown(f"""
    <div class="recipe-card">

        <span class="badge">
            Michelin Inspired
        </span>

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

                score = abs(1 - rec.get('score', 0))

                st.markdown(f"""
                <div class="rag-card">

                    <h4 style="
                        color:#f8e7b0;
                        margin-top:0;
                    ">
                        {rec['title']}
                    </h4>

                    <p style="
                        color:#d4af37;
                        font-size:14px;
                    ">
                        Match Score:
                        {score:.2f}
                    </p>

                </div>
                """, unsafe_allow_html=True)
