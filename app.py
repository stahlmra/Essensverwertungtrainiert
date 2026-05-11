import streamlit as st
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
# SESSION STATE
# =========================
if "title" not in st.session_state:
    st.session_state.title = None

if "data" not in st.session_state:
    st.session_state.data = None

if "rag" not in st.session_state:
    st.session_state.rag = []


# =========================
# STYLE
# =========================
st.markdown("""
<style>

.stApp {
    background: #0d0d0d;
    color: white;
}

.card {
    background: #151515;
    border: 1px solid #d4af37;
    border-radius: 20px;
    padding: 30px;
    margin-top: 20px;
}

.title {
    font-size: 40px;
    color: #d4af37;
    font-weight: 700;
    border-bottom: 2px solid #d4af37;
    display: inline-block;
    margin-bottom: 20px;
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

h3 {
    color: #d4af37;
}

.step {
    margin-bottom: 10px;
    padding-left: 10px;
    border-left: 2px solid #d4af37;
}

</style>
""", unsafe_allow_html=True)


# =========================
# UI
# =========================
st.title("🍽️ Michelin Chef AI")

ingredients_input = st.text_area("Enter ingredients (comma separated)")


# =========================
# GENERATE
# =========================
if st.button("⭐ Cook"):

    ingredients = [
        x.strip()
        for x in ingredients_input.split(",")
        if x.strip()
    ]

    if ingredients:

        title, data, rag = generate_chef_response(ingredients)

        st.session_state.title = title
        st.session_state.data = data
        st.session_state.rag = rag


# =========================
# OUTPUT (FIXED SAFE RENDERING)
# =========================
if st.session_state.data:

    data = st.session_state.data

    ingredients_html = "".join(
        f"<li>{i}</li>" for i in data["ingredients"]
    )

    steps_html = "".join(
        f"<div class='step'><b>Step {i+1}:</b> {s}.</div>"
        for i, s in enumerate(data["instructions"])
    )

    st.markdown(f"""
    <div class="card">

        <span class="badge">Michelin AI</span>

        <div class="title">
            {st.session_state.title}
        </div>

        <h3>🥘 Ingredients</h3>
        <ul>{ingredients_html}</ul>

        <h3>👨‍🍳 Instructions</h3>
        {steps_html}

    </div>
    """, unsafe_allow_html=True)
