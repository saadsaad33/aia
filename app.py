import streamlit as st
from google import genai
import PIL.Image
import os

# --- 1. APP CONFIG ---
st.set_page_config(page_title="AI Digital Stylist", layout="wide", page_icon="👗")
st.title("👗 AI Digital Stylist (2026 Edition)")

# --- 2. API KEY SECURITY ---
# This looks for GEMINI_API_KEY in your Streamlit Cloud Secrets vault
api_key = st.secrets.get("GEMINI_API_KEY")

# Sidebar for manual override and settings
with st.sidebar:
    st.header("Settings")
    
    # If the key isn't in secrets, show the input box
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")
        st.info("Get your key at aistudio.google.com")
    else:
        st.success("API Key loaded from Secrets ✅")

    model_choice = st.selectbox(
        "Select Model",
        ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
    )
    
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
    # Use columns that collapse well on mobile
    cols = st.columns([1, 1, 1, 1, 1])
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
            with st.spinner("Analyzing your wardrobe..."):
                try:
                    # System instruction tells the AI how to behave
                    sys_instr = "You are a professional fashion stylist. Use the provided images of clothing to suggest outfits. If no suitable clothing is found in the images, suggest what to buy to complete the look."
                    
                    response = client.models.generate_content(
                        model=model_choice,
                        contents=["Based on my closet images:", *images_for_ai, prompt],
                        config={"system_instruction": sys_instr}
                    )
                    
                    full_response = response.text
                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                except Exception as e:
                    st.error(f"Error: {e}")
else:
    st.info("👋 Welcome! Upload some photos of your clothes in the sidebar to start your digital closet.")
