import streamlit as st
from google import genai
import PIL.Image

# --- 1. APP CONFIG ---
st.set_page_config(page_title=" Digital Stylist", layout="wide", page_icon="👗")
st.title("👗  Digital Stylist 1.0")

# --- 2. API KEY SECURITY ---
# Prioritizes Streamlit Secrets for your deployed web app
api_key = st.secrets.get("GEMINI_API_KEY")

with st.sidebar:
    st.header("Settings")
    
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")
        st.info("Get your key at aistudio.google.com")
    else:
        st.success("API Key loaded from Secrets ✅")

    # UPDATED: Gemini 2.5 Flash is now the default
    model_choice = st.selectbox(
        "Select Model",
        ["gemini-2.5-flash", "gemini-3-flash", "gemini-2.0-flash"]
    )
    
    st.divider()
    uploaded_files = st.file_uploader(
        "Upload photos of your clothes", 
        accept_multiple_files=True, 
        type=['png', 'jpg', 'jpeg']
    )

# --- 3. VALIDATION ---
if not api_key:
    st.warning("Please enter your API Key in the sidebar or add it to Streamlit Secrets.")
    st.stop()

# Initialize Client
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Failed to connect: {e}")
    st.stop()

# --- 4. CLOSET SECTION ---
if uploaded_files:
    st.subheader("👕 Your Digital Closet")
    cols = st.columns(5)
    images_for_ai = []
    
    for i, file in enumerate(uploaded_files):
        img = PIL.Image.open(file)
        images_for_ai.append(img)
        with cols[i % 5]:
            st.image(img, use_container_width=True)

    st.divider()

    # --- 5. CHAT SECTION ---
    st.subheader("💬 Chat with your Stylist")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask: 'What can I wear for a business meeting?'"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner(f"Stylist is analyzing images with {model_choice}..."):
                try:
                    # PROMPT: Updated for the 2.5 Flash 'Agentic Vision' capabilities
                    sys_instr = (
                        "You are an AI Fashion Stylist with Agentic Vision. "
                        "Identify specific clothing items, colors, and textures from the images. "
                        "Create a complete outfit recommendation based ONLY on these items. "
                        "If an outfit is missing a key piece (like shoes), suggest a specific style to match."
                    )
                    
                    response = client.models.generate_content(
                        model=model_choice,
                        contents=["Closet contents:", *images_for_ai, f"User Request: {prompt}"],
                        config={"system_instruction": sys_instr}
                    )
                    
                    full_response = response.text
                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                except Exception as e:
                    st.error(f"API Error: {e}")
else:
    st.info("👋 Ready to style! Upload some photos of your clothes in the sidebar to begin.")


