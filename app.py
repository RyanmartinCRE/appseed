import streamlit as st
import google.generativeai as genai
import json
import os
from streamlit_lottie import st_lottie
from PIL import Image

# --- Setup Gemini ---
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# --- Load Local Lottie Animation ---
def load_lottie_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

banner_lottie = load_lottie_file("assets/banner.json")
st_lottie(banner_lottie, height=200, key="banner")

# --- Custom CSS for mobile-friendly layout ---
st.markdown("""
<style>
    html, body {
        margin: 0;
        padding: 0;
        background-color: #f4f6fa;
    }
    .stButton > button {
        background-color: #3ECF8E;
        color: white;
        padding: 0.6em 1.2em;
        border-radius: 8px;
        border: none;
    }
    .stTextInput > div > input {
        padding: 0.6em;
    }
</style>
""", unsafe_allow_html=True)

# --- App Title ---
st.markdown("""
<div style='text-align: center; padding-top: 10px;'>
    <h1 style='font-size: 2.5em;
        background: -webkit-linear-gradient(45deg, #3ECF8E, #0061ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2em;'>🌱 AppSeed</h1>
    <p style='color: #555; font-size: 1.1em;'>Plant your idea. Grow a full app plan.</p>
</div>
""", unsafe_allow_html=True)

# --- App Form ---
with st.form("app_idea_form"):
    category = st.selectbox("📂 Choose a category", [
        "Productivity", "Social", "Finance", "Health", "Education", "Fun / Playful", "AI / Tools", "Other"
    ])
    app_idea = st.text_area("💡 App Idea", placeholder="An AI-powered accountability buddy that keeps you focused...")
    target_audience = st.text_input("🎯 Target Audience (optional)")
    tone = st.radio("🎭 Tone", ["Serious", "Playful"], index=0)  # Flipped order
    submitted = st.form_submit_button("✨ Generate App Concept")

# --- Handle Submission ---
if submitted and app_idea.strip():
    with st.spinner("🌟 Cooking up your concept..."):
        prompt = f"""
You are a creative app concept generator designed to rapidly transform vague app ideas into detailed, actionable plans.

App Idea: {app_idea}
Category: {category}
Target Audience: {target_audience}
Tone: {tone}

Use this markdown-friendly output format:
- 🔤 **App Name & Tagline:**
- 📘 **Description:**
- 🧩 **Core Features (MVP):**
- 🚀 **Core Features (Full Version):**
- 👥 **Ideal Users:**
- 🧭 **User Flow Sketch:**
- 🛠️ **Technology Stack Suggestion (MVP):**

Keep it clear, inspiring, and great for a weekend build.
        """

        try:
            response = model.generate_content(prompt)
            st.session_state.result = response.text  # ✅ Store result in session
        except Exception as e:
            st.error("🚨 Error calling Gemini API:")
            st.exception(e)
            st.session_state.result = None

# --- Show Output if it exists ---
if "result" in st.session_state and st.session_state.result:
    st.markdown("### 💡 Your Generated Concept")

    view_mode = st.radio(
        "📄 View mode",
        options=["Preview", "Raw Markdown"],
        index=0,
        horizontal=False
    )

    if view_mode == "Preview":
        st.markdown(st.session_state.result)
    else:
        st.code(st.session_state.result, language="markdown")

    st.download_button("📄 Download as Markdown", st.session_state.result, file_name="app-concept.md")

    if st.button("💾 Save Idea Locally"):
        with open("saved_ideas.txt", "a", encoding="utf-8") as f:
            f.write(st.session_state.result + "\n\n---\n\n")
        st.success("Saved to saved_ideas.txt!")

    st.toast("Your app idea is ready! 🚀", icon="✨")
