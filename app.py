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

# --- Custom CSS for responsive layout ---
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
    .output-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        justify-content: center;
        margin-top: 1.5rem;
    }
    .output-box {
        background-color: white;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        width: 100%;
        max-width: 600px;
        flex: 1;
    }
    @media (min-width: 768px) {
        .output-box {
            width: 45%;
        }
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
    <p style='color: #555; font-size: 1.1em;'>Plant your idea. Grow full concepts side-by-side.</p>
</div>
""", unsafe_allow_html=True)

# --- App Form ---
with st.form("app_idea_form"):
    number_of_outputs = st.selectbox("🔢 How many formats do you want to generate?", [1, 2, 3])
    all_formats = ["App", "Chatbot", "Website"]
    selected_formats = st.multiselect("🛠️ Select output formats", all_formats, default=["App"], max_selections=number_of_outputs)
    category = st.selectbox("📂 Choose a category", [
        "Productivity", "Social", "Finance", "Health", "Education", "Fun / Playful", "AI / Tools", "Other"
    ])
    app_idea = st.text_area("💡 App Idea", placeholder="An AI-powered accountability buddy that keeps you focused...")
    target_audience = st.text_input("🎯 Target Audience (optional)")
    tone = st.radio("🎭 Tone", ["Serious", "Playful"], index=0)
    submitted = st.form_submit_button("✨ Generate Concepts")

# --- Prompt Generator ---
def generate_prompt(output_format, idea, category, audience, tone):
    if output_format == "App":
        return f"""
You are a creative app concept generator designed to rapidly transform vague app ideas into detailed, actionable plans.

App Idea: {idea}
Category: {category}
Target Audience: {audience}
Tone: {tone}

Use this markdown-friendly output format:
- 🔤 **App Name & Tagline:**
- 📘 **Description:**
- 🧩 **Core Features (MVP):**
- 🚀 **Core Features (Full Version):**
- 👥 **Ideal Users:**
- 🧭 **User Flow Sketch:**
- 🛠️ **Technology Stack Suggestion (MVP):**
- 🧠 **Tips You Might Not Have Considered:**
"""
    elif output_format == "Chatbot":
        return f"""
You are an expert chatbot architect. Take the idea below and turn it into a full chatbot concept.

Idea: {idea}
Category: {category}
Target Audience: {audience}
Tone: {tone}

Return a markdown-friendly response with:
- 🤖 **Chatbot Name & Personality:**
- 🎯 **Primary Use Cases:**
- 🧠 **Core Functions & Commands:**
- 💬 **Sample Conversations (with user & bot):**
- ⚠️ **Edge Cases & Error Handling:**
- 🧠 **Tips You Might Not Have Considered:**
"""
    elif output_format == "Website":
        return f"""
You're a creative full-stack strategist helping someone turn an idea into a fully structured website using Streamlit-style workflows.

Website Idea: {idea}
Category: {category}
Target Audience: {audience}
Tone: {tone}

Return this markdown format:
- 🌐 **Website Name & Purpose:**
- 📄 **Pages & Workflow Overview:**
- 🧩 **Core Interactions & UI Elements:**
- 🛠️ **Recommended Tech Stack:**
- ⚙️ **Streamlit-Like Features to Include:**
- 🧠 **Tips You Might Not Have Considered:**
"""

# --- Generate & Store Responses ---
if submitted and app_idea.strip():
    with st.spinner("🌟 Generating your concepts..."):
        st.session_state.results = {}
        for fmt in selected_formats:
            prompt = generate_prompt(fmt, app_idea, category, target_audience, tone)
            try:
                response = model.generate_content(prompt)
                full_result = f"### 🛠️ Output Format: {fmt}\n\n{response.text}"
                st.session_state.results[fmt] = full_result
            except Exception as e:
                st.session_state.results[fmt] = f"❌ Error generating {fmt}:\n```\n{e}\n```"

# --- Display Results ---
if "results" in st.session_state and st.session_state.results:
    st.markdown("## 💡 Your Generated Concepts")

    st.markdown("<div class='output-container'>", unsafe_allow_html=True)

    for fmt in st.session_state.results:
        key_base = fmt.lower().replace(" ", "_")
        result = st.session_state.results[fmt]
        with st.container():
            st.markdown(f"<div class='output-box'>", unsafe_allow_html=True)
            view_mode = st.radio(
                f"📄 View mode for {fmt}",
                ["Preview", "Raw Markdown"],
                key=f"{key_base}_view",
                horizontal=False
            )

            if view_mode == "Preview":
                st.markdown(result)
            else:
                st.code(result, language="markdown")

            st.download_button(f"📥 Download {fmt}", result, file_name=f"{key_base}_concept.md", key=f"{key_base}_dl")

            if st.button(f"💾 Save {fmt} Locally", key=f"{key_base}_save"):
                with open("saved_ideas.txt", "a", encoding="utf-8") as f:
                    f.write(result + "\n\n---\n\n")
                st.success(f"{fmt} saved!")

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
