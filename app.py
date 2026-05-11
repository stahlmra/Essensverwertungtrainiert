import streamlit as st
import os

from backend.img_ingred_detection import extract_ingredients
from backend.recipe_generator import generate_chef_response


# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Michelin Chef AI",
    page_icon="⭐",
    layout="centered"
)


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

.stApp {
    background: #0d0d0d;
    color: white;
}

.recipe-card {
    background: #151515;
    border: 1px solid #d4af37;
    border-radius: 20px;
    padding: 30px;
    margin-top: 20px;
}

.recipe-title {
    font-size: 40px;
    color: #d4af37;
    font-weight: bold;
    margin-bottom: 15px;
    border-bottom: 2px solid #d4af37;
    display: inline-block;
}

.badge {
    float: right;
    background: #d4af37;
    color: black;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: bold;
}

.step {
    margin-bottom: 10px;
    padding-left: 10px;
    border-left: 2px solid #d4af37;
}

h3 {
    color: #d4af37;
}

</style>
""", unsafe_allow_html=True)


# =========================
# HEADER
# =========================
st.title("🍽️ Michelin Chef AI")


# =========================
# INPUT
# =========================
ingredients_input = st.text_area(
    "Ingredients (comma separated)",
    value=st.session_state.ingredients_list
)

st.session_state.ingredients_list = ingredients_input


# =========================
# GENERATE
# =========================
if st.button("⭐ Create Dish"):

    ingredients_clean = [
        x.strip()
        for x in ingredients_input.split(",")
        if x.strip()
    ]

    if not ingredients_clean:
        st.error("Please enter ingredients")
    else:
        title, body, rag = generate_chef_response(
            ingredients_clean
        )

        st.session_state.recipe_title = title
        st.session_state.recipe_body = body
        st.session_state.rag_recommendations = rag

        st.rerun()


# =========================
# OUTPUT (IMPORTANT FIX)
# =========================
if st.session_state.recipe_body:

    st.markdown(f"""
    <div class="recipe-card">

        <span class="badge">Michelin AI</span>

        <div class="recipe-title">
            {st.session_state.recipe_title}
        </div>

        {st.session_state.recipe_body}

    </div>
    """, unsafe_allow_html=True)
