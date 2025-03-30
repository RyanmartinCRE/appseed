import streamlit as st
import google.generativeai as genai
import json
import os
import urllib.parse
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
        margin: 0;
        padding: 0;
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
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        width: 100%;
    }
    .banner-bg {
        background: linear-gradient(120deg, #3ECF8E, #0061ff);
        border-radius: 20px;
        padding: 1.5rem 1rem;
        margin-bottom: 1.5rem;
        text-align: center;
        color: white;
    }
    @media (max-width: 768px) {
        .output-box {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Optional Load from Shared JSON ---
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
        <h1 style='font-size: 2.5em; margin: 0;'>🌱 AppSeed</h1>
        <p style='font-size: 1.1em;'>Plant your idea. Grow full concepts side-by-side.</p>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Form ---
with st.form("app_idea_form"):
    st.markdown("### 🧠 Describe Your Idea")
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
        return f"""You are a creative app concept generator...

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
- 🛠️ **Tech Stack:**
- 🧠 **Tips You Might Not Have Considered:**"""
    elif fmt == "Chatbot":
        return f"""You are an expert chatbot architect...

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
        return f"""You're a full-stack strategist helping someone build a site...

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

            # View toggle now BELOW preview
            view_mode = st.radio(
                f"📄 View mode for {fmt}",
                ["Preview", "Raw Markdown"],
                key=f"{key_base}_view",
                index=0,
                horizontal=True
            )
            if view_mode == "Raw Markdown":
                st.code(result, language="markdown")

            st.download_button(f"📥 Download {fmt}", result, file_name=f"{key_base}_concept.md", key=f"{key_base}_dl")

            if st.button(f"💾 Save {fmt} Locally", key=f"{key_base}_save"):
                with open("saved_ideas.txt", "a", encoding="utf-8") as f:
                    f.write(result + "\n\n---\n\n")
                st.success(f"{fmt} saved!")

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Share Button at Bottom ---
    if st.button("🔗 Share This Page"):
        share_payload = {
            "inputs": st.session_state.inputs,
            "results": st.session_state.results
        }
        share_str = urllib.parse.quote(json.dumps(share_payload))
        share_url = f"{st.request.url}?data={share_str}"
        st.code(share_url, language="text")
        st.success("📤 Share this URL to let others see your results!")

    st.download_button("💾 Download Full Session JSON", json.dumps({
        "inputs": st.session_state.inputs,
        "results": st.session_state.results
    }, indent=2), file_name="appseed_session.json")

