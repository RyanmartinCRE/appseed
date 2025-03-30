import streamlit as st
import google.generativeai as genai
import json
import os
import urllib.parse
import datetime
from streamlit_lottie import st_lottie
from PIL import Image

# --- Setup Gemini ---
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# --- Load Lottie ---
def load_lottie_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

banner_lottie = load_lottie_file("assets/banner.json")

# --- Custom CSS ---
st.markdown("""
<style>
    html, body {
        background-color: #f5f7fb;
        font-family: 'Segoe UI', sans-serif;
        line-height: 1.6;
    }
    .stButton > button {
        background-color: #3ECF8E;
        color: white;
        padding: 0.6em 1.2em;
        border-radius: 8px;
        border: none;
        font-weight: 600;
    }
    .output-container {
        display: flex;
        flex-direction: column;
        gap: 2rem;
        margin-top: 2rem;
    }
    .output-box {
        background-color: white;
        padding: 2%;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        width: 96%;
        margin: 0 auto;
    }
    .banner-bg {
        background: linear-gradient(120deg, rgba(62,207,142,0.25), rgba(0,97,255,0.25));
        border-radius: 20px;
        padding: 2rem 1rem;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    h1, h2, h3, h4 {
        line-height: 1.2;
    }
    hr {
        border: none;
        border-top: 1px solid #ddd;
        margin: 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Optional: Load Shared Data from URL ---
shared_data = st.query_params.get("data")
if shared_data:
    try:
        loaded_data = json.loads(urllib.parse.unquote(shared_data))
        st.session_state.inputs = loaded_data.get("inputs", {})
        st.session_state.results = loaded_data.get("results", {})
        st.success("✅ Loaded shared session!")
    except Exception:
        st.warning("⚠️ Failed to load shared data.")

# --- Banner ---
with st.container():
    st.markdown("<div class='banner-bg'>", unsafe_allow_html=True)
    st_lottie(banner_lottie, height=150, key="banner")
    st.markdown("""
        <h1>🌱 AppSeed</h1>
        <p style='font-size: 1.1em;'>Plant your idea. Grow full concepts side-by-side.</p>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Inputs Form ---
st.markdown("## 🧠 Describe Your Idea")
with st.form("app_idea_form"):
    all_formats = ["App", "Chatbot", "Website"]
    selected_formats = st.multiselect("🛠️ Select output formats", all_formats, default=["App"])

    category = st.selectbox("📂 Choose a category", [
        "Productivity", "Social", "Finance", "Health", "Education", "Fun / Playful", "AI / Tools", "Other"
    ])
    app_idea = st.text_area("💡 App Idea", placeholder="An AI-powered accountability buddy that keeps you focused...")
    target_audience = st.text_input("🎯 Target Audience (optional)")
    tone = st.radio("🎭 Tone", ["Serious", "Playful"], index=0)

    uploaded_json = st.file_uploader("📂 Load Shared AppSeed JSON (optional)", type=["json"])
    submitted = st.form_submit_button("✨ Generate Concepts")

    if uploaded_json:
        try:
            data = json.load(uploaded_json)
            st.session_state.inputs = data.get("inputs", {})
            st.session_state.results = data.get("results", {})
            st.experimental_rerun()
        except:
            st.warning("⚠️ Failed to load file.")

    if submitted:
        if not app_idea.strip():
            st.warning("⚠️ Please enter an app idea.")
            st.stop()
        if not selected_formats:
            st.warning("⚠️ Select at least one output format.")
            st.stop()

        st.session_state.inputs = {
            "app_idea": app_idea,
            "category": category,
            "target_audience": target_audience,
            "tone": tone,
            "selected_formats": selected_formats
        }

# --- Prompt Generator ---
def generate_prompt(fmt, idea, category, audience, tone):
    if fmt == "App":
        return f"""
You are a creative app concept generator...

App Idea: {idea}
Category: {category}
Target Audience: {audience}
Tone: {tone}

Return:
- 🔤 **App Name & Tagline:**
- 📘 **Description:**
- 🧩 **Core Features (MVP):**
- 🚀 **Core Features (Full Version):**
- 👥 **Ideal Users:**
- 🧭 **User Flow Sketch:**
- 🛠️ **Technology Stack Suggestion (MVP):**
- 🧠 **Tips You Might Not Have Considered:**"""
    elif fmt == "Chatbot":
        return f"""
You are an expert chatbot architect...

Idea: {idea}
Category: {category}
Target Audience: {audience}
Tone: {tone}

Return:
- 🤖 **Chatbot Name & Personality:**
- 🎯 **Use Cases:**
- 🧠 **Functions:**
- 💬 **Sample Dialogues:**
- ⚠️ **Edge Cases:**
- 🧠 **Tips:**"""
    elif fmt == "Website":
        return f"""
You're a full-stack strategist helping someone build a site...

Website Idea: {idea}
Category: {category}
Target Audience: {audience}
Tone: {tone}

Return:
- 🌐 **Name & Purpose:**
- 📄 **Pages & Workflow:**
- 🧩 **UI Elements:**
- 🛠️ **Tech Stack:**
- ⚙️ **Features:**
- 🧠 **Tips:**"""

# --- Generate Results ---
if submitted and st.session_state.inputs:
    with st.spinner("✨ Generating concepts..."):
        st.session_state.results = {}
        for fmt in st.session_state.inputs["selected_formats"]:
            prompt = generate_prompt(
                fmt,
                st.session_state.inputs["app_idea"],
                st.session_state.inputs["category"],
                st.session_state.inputs["target_audience"],
                st.session_state.inputs["tone"]
            )
            try:
                response = model.generate_content(prompt)
                result_text = f"### 🛠️ Output Format: {fmt}\n\n{response.text}"
                st.session_state.results[fmt] = result_text
            except Exception as e:
                st.session_state.results[fmt] = f"❌ Error generating {fmt}:\n```\n{e}\n```"

# --- Display Outputs ---
if st.session_state.get("results"):
    st.markdown("## 💡 Your Generated Concepts")
    st.markdown("<div class='output-container'>", unsafe_allow_html=True)

    for fmt in st.session_state.results:
        key_base = fmt.lower().replace(" ", "_")
        result = st.session_state.results[fmt]

        with st.container():
            st.markdown("<div class='output-box'>", unsafe_allow_html=True)
            st.markdown(result, unsafe_allow_html=True)

            view_mode = st.radio(
                f"📄 View mode for {fmt}",
                ["Preview", "Raw Markdown"],
                key=f"{key_base}_view",
                index=0,
                horizontal=True
            )

            if view_mode == "Raw Markdown":
                st.code(result, language="markdown")

            st.download_button(
                f"📥 Download {fmt}",
                result,
                file_name=f"{key_base}_concept.md",
                key=f"{key_base}_dl"
            )

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            if st.button(f"💾 Save {fmt} Locally", key=f"{key_base}_save"):
                filename = f"saved_idea_{fmt}_{timestamp}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(result)
                st.success(f"Saved to {filename}")

            # 📋 Fancy Copy Button
            st.markdown(f"""
                <textarea id="copy_target_{key_base}" style="opacity:0; position:absolute;">{result}</textarea>
                <button onclick="navigator.clipboard.writeText(document.getElementById('copy_target_{key_base}').value)" style="
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    padding: 0.4em 1em;
                    border-radius: 6px;
                    font-weight: bold;
                    cursor: pointer;
                    margin-top: 10px;
                ">📋 Copy to Clipboard</button>
            """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Share + Download Full Session ---
    if st.button("🔗 Share This Page"):
        share_payload = {
            "inputs": st.session_state.inputs,
            "results": st.session_state.results
        }
        share_str = urllib.parse.quote(json.dumps(share_payload))
        st.markdown(f"[🔗 Click here to share this link](?data={share_str})")
        st.success("📤 Share link created!")

    st.download_button(
        "💾 Download Full Session JSON",
        json.dumps({
            "inputs": st.session_state.inputs,
            "results": st.session_state.results
        }, indent=2),
        file_name=f"appseed_session_{datetime.datetime.now().strftime('%Y-%m-%d')}.json"
    )
