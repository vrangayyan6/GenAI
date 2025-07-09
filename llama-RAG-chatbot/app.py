# File: app.py
# This is a simple Streamlit app that uses the Llama 3.2 model via Ollama and apply RAG using ChromaDB to create a chatbot interface.
# python -m venv llama-venv
# .\llama-venv\Scripts\activate
# install Ollama first from https://ollama.com/
# curl -fsSL https://ollama.com/install.sh | sh
# ollama run llama3.2:1b
# pip install -r requirements.txt
# streamlit run app.py


import streamlit as st
from src.chatbot import Chatbot

@st.cache_resource
def load_chatbot():
    """Loads the chatbot model and caches it."""
    chatbot = Chatbot()
    chatbot.load_model()
    return chatbot

st.title("Llama 3.2 RAG Chatbot")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

chatbot = load_chatbot()

# Accept user input
if prompt := st.chat_input("What would you like to ask?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Generate and display assistant response
    with st.chat_message("assistant"):
        response = st.write_stream(chatbot.stream_response(prompt))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
