import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the app
st.set_page_config(
    page_title="RAG Chat Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

# Backend API URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def query_backend(message):
    """Send a query to the backend and get the response."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/ask",
            json={"query": message}
        )
        response.raise_for_status()
        return response.json()["answer"]
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with backend: {str(e)}")
        return None

# App title
st.title("🤖 RAG Chat Assistant")

# Description
st.markdown("""
This chat interface allows you to interact with documents that have been ingested into the system.
Ask questions about the content, and the AI will provide relevant answers based on the stored knowledge.
""")

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = query_backend(prompt)
            if response:
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    This is a RAG-powered chat interface that allows you to:
    - Ask questions about ingested documents
    - Get AI-generated responses based on the document content
    - Have natural conversations about the stored knowledge
    """)
    
    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun() 