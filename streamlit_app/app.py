import streamlit as st
import os
from dotenv import load_dotenv
import openai
from openai import OpenAI
from anthropic import Anthropic
import json

# Load environment variables
load_dotenv()

def initialize_session_state():
    """Initialize session state variables."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'api_keys' not in st.session_state:
        st.session_state.api_keys = {}

def get_api_key(model_provider):
    """Get API key from input or environment variable."""
    api_key = st.session_state.api_keys.get(model_provider)
    
    if not api_key:
        # Try to get from environment
        if model_provider == "OpenAI":
            api_key = os.getenv("OPENAI_API_KEY", "")
        elif model_provider == "Anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
    
    return api_key

def get_ai_response(message, model_provider, selected_model, api_key):
    """Get response from selected AI model."""
    try:
        if model_provider == "OpenAI":
            client = OpenAI()
            client.api_key = api_key
            response = client.chat.completions.create(
                model=selected_model,
                messages=st.session_state.chat_history
            )
            return response.choices[0].message.content
        
        elif model_provider == "Anthropic":
            anthropic = Anthropic(api_key=api_key)
            response = anthropic.messages.create(
                model=selected_model,
                messages=st.session_state.chat_history
            )
            return response.content
        
        else:
            return "Unsupported model selected"
    
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    st.title("🤖 AI Chatbot")
    
    initialize_session_state()
    
    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")
        
        # Model selection
        models = {
            "OpenAI": ["gpt-3.5-turbo", "gpt-4"],
            "Anthropic": ["claude-3-opus", "claude-3-sonnet"]
        }
        
        model_provider = st.selectbox("Select Provider", list(models.keys()))
        selected_model = st.selectbox("Select Model", models[model_provider])
        
        # API Key input
        api_key = st.text_input(
            f"{model_provider} API Key",
            type="password",
            help=f"Enter your {model_provider} API key or leave blank to use value from .env file"
        )
        
        if api_key:
            st.session_state.api_keys[model_provider] = api_key
    
    # Chat interface
    st.header("Chat")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if user_input := st.chat_input("Type your message here..."):
        # Get API key
        api_key = get_api_key(model_provider)
        
        if not api_key:
            st.error(f"Please provide an API key for {model_provider} either in the sidebar or in the .env file")
            return
        
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Get AI response
        with st.spinner("Thinking..."):
            ai_response = get_ai_response(user_input, model_provider, selected_model, api_key)
            
            # Add AI response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        # Rerun to update chat display
        st.rerun()

    # Add a button to clear chat history
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

if __name__ == "__main__":
    main()