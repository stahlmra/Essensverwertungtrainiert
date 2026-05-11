import streamlit as st
from PIL import Image
import io
import os

from backend.img_ingred_detection import extract_ingredients
from backend.recipe_generator import generate_chef_response


# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Benes Geheimrezepte",
    page_icon="👨‍🍳",
    layout="centered"
)


# --- DATABASE CHECK ---
if not os.path.exists("./chroma_db"):
    try:
        if os.path.exists("scripts/seed_chroma.py"):
            st.toast("🌱 First run: Seeding database...", icon="⚙️")
            from scripts.seed_chroma import seed
            seed()
    except Exception:
        pass


# --- SESSION STATE ---
if "ingredients_list" not in st.session_state:
    st.session_state.ingredients_list = ""

if "recipe_title" not in st.session_state:
    st.session_state.recipe_title = None

if "recipe_body" not in st.session_state:
    st.session_state.recipe_body = None

if "rag_recommendations" not in st.session_state:
    st.session_state.rag_recommendations = []


# --- PROFESSIONAL CSS THEME ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@400;700&display=swap');

    .stApp { background-color: #fcfbf9; }

    .recipe-card {
        background: white;
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
        margin-bottom: 30px;
        font-family: 'Lato', sans-serif;
        color: #333;
    }

    .recipe-title {
        color: #2c3e50;
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        margin-bottom: 15px;
        line-height: 1.2;
        border-bottom: 3px solid #FFD700;
        display: inline-block;
        padding-bottom: 5px;
    }

    .recipe-desc {
        font-size: 1.1rem;
        color: #555;
        font-style: italic;
        margin-bottom: 20px;
        background: #f9f9f9;
        padding: 15px;
        border-left: 4px solid #FFD700;
        border-radius: 4px;
    }

    .label {
        font-weight: 800;
        color: #000;
        text-transform: uppercase;
        font-size: 0.9rem;
        letter-spacing: 0.5px;
        margin-right: 5px;
    }

    .recipe-meta {
        font-size: 0.95rem;
        color: #777;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 25px;
    }

    h3 {
        font-family: 'Playfair Display', serif;
        color: #333;
        margin-top: 25px;
        margin-bottom: 15px;
        font-size: 1.5rem;
    }

    li { margin-bottom: 8px; line-height: 1.6; }

    .step {
        margin-bottom: 12px;
        line-height: 1.6;
    }

    .badge {
        background: #333;
        color: #fff;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        float: right;
        margin-top: -10px;
    }

    .rag-card {
        background: white;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #eee;
        height: 100%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }
</style>
""", unsafe_allow_html=True)


# --- MAIN UI ---
st.title("👨‍🍳 AI Chef Pro")
st.write("Upload a photo or enter ingredients to generate a chef-quality recipe.")


# --- SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    prefs = st.text_input("Dietary Preferences", placeholder="e.g. Vegetarian, Keto")
    st.info("💡 **Tip:** Ensure good lighting for better detection.")


# --- INPUT TABS ---
tabs = st.tabs(["📸 Photo Input", "📝 Manual Input"])


# TAB 1: PHOTO INPUT
with tabs[0]:
    uploaded = st.file_uploader("Upload Pantry Photo", type=["jpg", "png", "jpeg"])

    if uploaded:
        st.image(uploaded, caption="Uploaded Image", width="stretch")

        if st.button("🔍 Detect Ingredients", key="btn_detect"):
            with st.spinner("Analyzing image..."):
                uploaded.seek(0)
                img_bytes = uploaded.read()
                detected = extract_ingredients(img_bytes)

                if detected:
                    st.session_state.ingredients_list = ", ".join(detected)
                    st.success(f"Detected {len(detected)} items!")
                else:
                    st.warning("No ingredients detected. Please type manually.")
                    st.session_state.ingredients_list = ""

            st.rerun()


# TAB 2: MANUAL INPUT
with tabs[1]:
    st.write("Type ingredients manually if you don't have a photo.")


# --- EDITING & GENERATION ---
st.divider()
st.subheader("✅ Confirm Ingredients")

final_ingredients_str = st.text_area(
    "Edit list before generating:",
    value=st.session_state.ingredients_list,
    placeholder="e.g. tomato, onion, chicken...",
    help="Add missing items or remove errors here."
)

st.session_state.ingredients_list = final_ingredients_str


if st.button("🔥 Cook Now!", type="primary"):

    ingredients_clean = [
        x.strip()
        for x in final_ingredients_str.split(",")
        if x.strip()
    ]

    if not ingredients_clean:
        st.error("Please enter at least one ingredient.")
    else:
        with st.spinner("👨‍🍳 The Chef is designing your recipe..."):
            title, body, rag_recs = generate_chef_response(ingredients_clean, prefs)

            st.session_state.recipe_title = title
            st.session_state.recipe_body = body
            st.session_state.rag_recommendations = rag_recs

        st.rerun()


# --- RESULTS DISPLAY ---
if st.session_state.recipe_body:

    st.divider()

    st.markdown(f"""
    <div class='recipe-card'>

        <span class='badge'>AI Generated</span>

        <div class='recipe-title'>
            {st.session_state.recipe_title}
        </div>

        {st.session_state.recipe_body}

    </div>
    """, unsafe_allow_html=True)


    if st.session_state.rag_recommendations:

        st.subheader("📚 Inspired by the Cookbook")

        cols = st.columns(len(st.session_state.rag_recommendations))

        for idx, rec in enumerate(st.session_state.rag_recommendations):

            with cols[idx]:
                st.markdown(f"""
                <div class='rag-card'>

                    <h4 style='margin:0; color:#333;'>
                        {rec['title']}
                    </h4>

                    <p style='color:#27ae60; font-weight:bold; font-size:0.8rem; margin-bottom:10px;'>
                        Match Score: {1 - rec['score']:.2f}
                    </p>

                    <details>
                        <summary style='cursor:pointer; color:#777;'>
                            View Snippet
                        </summary>
                        <p style='color:#555; font-size:0.85rem; margin-top:5px; line-height:1.4;'>
                            {rec['recipe_text'][:250]}...
                        </p>
                    </details>

                </div>
                """, unsafe_allow_html=True)
