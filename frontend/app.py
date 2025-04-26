import os

import requests
import streamlit as st
from dotenv import load_dotenv
from google_credential_file_generator import get_google_credentials
from streamlit_google_auth import Authenticate

# Load environment variables
load_dotenv()

# Configure the app
st.set_page_config(page_title="RAG Chat Assistant", page_icon="🤖", layout="wide")

# Custom CSS for buttons and login page
st.markdown(
    """
    <style>
    /* Regular button styles */
    button[kind="primary"] {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
    }
    button[kind="primary"]:hover {
        background-color: #45a049;
    }
    button[kind="primary"]:active {
        background-color: #3d8b40;
    }
    
    /* Clear Chat button styles */
    button[kind="secondary"] {
        background-color: #dc3545 !important;
        color: white !important;
    }
    button[kind="secondary"]:hover {
        background-color: #c82333 !important;
    }
    button[kind="secondary"]:active {
        background-color: #bd2130 !important;
    }
            
    button[kind="tertiary"] {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
    }
            
    button[kind="tertiary"]:hover {
        background-color: #45a049;
    }
    button[kind="tertiary"]:active {
        background-color: #3d8b40;
    }
    
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 4rem 2rem;
        margin: 2rem auto;
        max-width: 800px;
    }
    .login-title {
        color: #ffffff;
        font-size: 3rem;
        margin-bottom: 1.5rem;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .login-description {
        color: #ffffff;
        text-align: center;
        margin-bottom: 3rem;
        font-size: 1.2rem;
        line-height: 1.6;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        opacity: 0.9;
    }
    .login-features {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-bottom: 3rem;
    }
    .feature-card {
        background: rgba(255, 255, 255, 0.15);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        flex: 1;
        max-width: 200px;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .feature-title {
        color: #ffffff;
        font-weight: bold;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    .feature-description {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.9rem;
        line-height: 1.4;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Constants for file upload
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {
    "pdf": "PDF Document",
}

authenticator = Authenticate(
    secret_credentials_path=get_google_credentials(),
    cookie_name="my_cookie_name",
    cookie_key="this_is_secret",
    redirect_uri="http://localhost:8501",
)

# Check if the user is already authenticated
authenticator.check_authentification()

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

# Backend API URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


# Get authentication headers
def get_auth_headers():
    return {"X-API-KEY": os.getenv("BACKEND_API_KEY")}


def query_backend(message, user_email):
    """Send a query to the backend and get the response."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/ask",
            json={"query": message, "user_email": user_email},
            headers=get_auth_headers(),
        )
        response.raise_for_status()
        return response.json()["answer"]
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with backend: {str(e)}")
        return None


def upload_file(file, user_email):
    """Upload a file to the backend."""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        data = {"user_email": user_email}
        response = requests.post(
            f"{BACKEND_URL}/ingest", files=files, data=data, headers=get_auth_headers()
        )
        response.raise_for_status()
        return True, "File ingested successfully!"
    except requests.exceptions.RequestException as e:
        return False, f"Error ingesting file: {str(e)}"


def validate_file(file):
    """Validate the uploaded file."""
    if file.size > MAX_FILE_SIZE:
        return (
            False,
            f"File size exceeds the maximum limit of {MAX_FILE_SIZE/1024/1024}MB",
        )

    file_extension = file.name.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return (
            False,
            f"File type not supported. Allowed types: {', '.join(ALLOWED_EXTENSIONS.keys())}",
        )

    return True, "File is valid"


# App title
st.title("🤖 RAG Chat Assistant")

# Login page
if not st.session_state.get("connected", False):
    st.markdown(
        """
        <div class="login-container">
            <h1 class="login-title">Welcome to RAG Chat Assistant</h1>
            <p class="login-description">
                Your intelligent document analysis and question-answering system.<br>
                Upload your documents and get instant answers to your questions.
            </p>
            <div class="login-features">
                <div class="feature-card">
                    <div class="feature-icon">📚</div>
                    <div class="feature-title">Document Analysis</div>
                    <div class="feature-description">Upload and analyze your documents with AI</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">💬</div>
                    <div class="feature-title">Smart Chat</div>
                    <div class="feature-description">Ask questions and get intelligent responses</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔍</div>
                    <div class="feature-title">Deep Search</div>
                    <div class="feature-description">Find relevant information quickly</div>
                </div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([3, 2, 3])
    authorization_url = authenticator.get_authorization_url()
    with col2:
        st.link_button(
            "Login with Google",
            authorization_url,
            use_container_width=True,
            type="primary",
        )
else:
    # Create two columns for the Clear Chat button
    col1, col2 = st.columns([7, 1])
    with col2:
        if st.button("Clear Chat", use_container_width=True, type="secondary"):
            st.session_state.messages = []
            st.rerun()

    # Description
    st.markdown(
        """
    This chat interface allows you to interact with documents that have been ingested into the system.
    Ask questions about the content, and the AI will provide relevant answers based on the stored knowledge.
    """
    )

    # Get user email
    user_email = st.session_state["user_info"].get("email")

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
                response = query_backend(prompt, user_email)
                if response:
                    st.markdown(response)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )

    # Sidebar
    with st.sidebar:
        # user info
        st.image(st.session_state["user_info"].get("picture"))
        st.write(f"Hello, {st.session_state['user_info'].get('name')}")
        st.write(st.session_state["user_info"].get("email"))

        # About Section
        st.markdown("### 📚 About")
        st.markdown(
            """
        This is a RAG-powered chat interface that allows you to:
        - Ask questions about ingested documents
        - Get AI-generated responses based on the document content
        - Have natural conversations about the stored knowledge
        """
        )

        st.divider()

        # File Upload Section
        st.markdown("### 📤 Upload Document")
        st.markdown(
            f"""
        Add new documents to the knowledge base:
        - Supported: {', '.join(ALLOWED_EXTENSIONS.keys())}
        - Max size: {MAX_FILE_SIZE/1024/1024}MB
        """
        )

        uploaded_file = st.file_uploader(
            "Choose a file",
            type=list(ALLOWED_EXTENSIONS.keys()),
            help=f"Maximum file size: {MAX_FILE_SIZE/1024/1024}MB",
        )

        if uploaded_file is not None:
            # Validate file
            is_valid, message = validate_file(uploaded_file)
            if is_valid:
                # Add upload button
                if st.button("Upload File", use_container_width=True, type="primary"):
                    # Upload file
                    with st.spinner("Uploading file..."):
                        success, message = upload_file(uploaded_file, user_email)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
            else:
                st.error(message)

        st.divider()

        # Logout button
        if st.button("Logout", use_container_width=True, type="primary"):
            st.session_state.messages = []
            authenticator.logout()
