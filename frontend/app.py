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

# Custom CSS for buttons
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #45a049;
    }
    div.stButton > button:active {
        background-color: #3d8b40;
    }
    </style>
""", unsafe_allow_html=True)

# Constants for file upload
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {
    'pdf': 'PDF Document',
}

USER_ID = "123456"

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

# Backend API URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def query_backend(message):
    """Send a query to the backend and get the response."""
    try:
        data = {'query': message, 'user_id': USER_ID}
        response = requests.post(
            f"{BACKEND_URL}/ask",
            json=data
        )
        response.raise_for_status()
        return response.json()["answer"]
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with backend: {str(e)}")
        return None

def upload_file(file):
    """Upload a file to the backend."""
    try:
        files = {'file': (file.name, file.getvalue(), file.type)}
        data = {'user_id': USER_ID}
        response = requests.post(
            f"{BACKEND_URL}/ingest",
            files=files,
            data=data
        )
        response.raise_for_status()
        return True, "File ingested successfully!"
    except requests.exceptions.RequestException as e:
        return False, f"Error ingesting file: {str(e)}"

def validate_file(file):
    """Validate the uploaded file."""
    if file.size > MAX_FILE_SIZE:
        return False, f"File size exceeds the maximum limit of {MAX_FILE_SIZE/1024/1024}MB"
    
    file_extension = file.name.split('.')[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return False, f"File type not supported. Allowed types: {', '.join(ALLOWED_EXTENSIONS.keys())}"
    
    return True, "File is valid"

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
    # About Section
    st.markdown("### 📚 About")
    st.markdown("""
    This is a RAG-powered chat interface that allows you to:
    - Ask questions about ingested documents
    - Get AI-generated responses based on the document content
    - Have natural conversations about the stored knowledge
    """)
    
    st.divider()
    
    # File Upload Section
    st.markdown("### 📤 Upload Document")
    st.markdown(f"""
    Add new documents to the knowledge base:
    - Supported: {', '.join(ALLOWED_EXTENSIONS.keys())}
    - Max size: {MAX_FILE_SIZE/1024/1024}MB
    """)
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=list(ALLOWED_EXTENSIONS.keys()),
        help=f"Maximum file size: {MAX_FILE_SIZE/1024/1024}MB"
    )
    
    if uploaded_file is not None:
        # Validate file
        is_valid, message = validate_file(uploaded_file)
        if is_valid:
            # Add upload button
            if st.button("Upload File", use_container_width=True):
                # Upload file
                with st.spinner("Uploading file..."):
                    success, message = upload_file(uploaded_file)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        else:
            st.error(message)
    
    st.divider()
    
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun() 