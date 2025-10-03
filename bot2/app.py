# app.py

import os
import gspread
import pandas as pd
from datetime import datetime
from typing import TypedDict, Annotated, List
from dotenv import load_dotenv

import gradio as gr
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
# from google import genai
# from google.genai import types
# import warnings
# from google.api_core import exceptions as api_exceptions

import google.generativeai as genai
from google.generativeai import GenerativeModel

import warnings
# --- 1. Load Environment Variables and Initial Setup ---
load_dotenv()

# --- Configuration ---
DB_DIR = os.path.join(os.path.dirname(__file__), "db")
GSHEET_ID = os.getenv("GSHEET_ID")
SERVICE_ACCOUNT_FILE = 'service_account.json'
model_to_use = os.getenv("MODEL_TO_USE")
embedding_to_use = os.getenv("EMBEDDING_TO_USE")


# def show_available_models():
#     avl_models = []
#     try:
#         client = genai.Client()
#         avl_models = client.list_models()

#         # List the available models
#         avl_models = client.models.list()

#         # Iterate and print information about each model
#         for model in avl_models:
#             print(f"Model Name: {model.name}")
#             print(f"Description: {model.description}")
#             # print(f"Input Modalities: {model.input_modalities}")
#             # print(f"Output Modalities: {model.output_modalities}")
#             # print("-" * 20)
#     except Exception as e:
#         print(f"Could not list models from genai: {e}")

#     return avl_models

# print("show_available_models:", show_available_models())

# --- Initialize models and vector store ---
print("Initializing models and vector store...")
# llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
# embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

try:
    llm = ChatGoogleGenerativeAI(model=model_to_use, temperature=0.7)
    # Choose embedding function. The sync script (`sync_vectordb.py`) uses
    # HuggingFaceEmbeddings (default: sentence-transformers/all-MiniLM-L6-v2)
    # which produces 384-dimensional vectors. If a persisted Chroma DB
    # already exists in `DB_DIR`, prefer HuggingFace so dimensions match and
    # avoid errors like "Collection expecting embedding with dimension of 384, got 768".
    hf_model = os.getenv("HUGGINGFACE_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    hf_device = os.getenv("EMBEDDING_DEVICE", "cpu")

    # If a Chroma DB was persisted locally, prefer the HF embedding to match it.
    chroma_db_file = os.path.join(DB_DIR, "chroma.sqlite3")
    if os.path.exists(chroma_db_file):
        print("Detected existing Chroma DB. Using HuggingFaceEmbeddings to match persisted vectors.")
        embeddings = HuggingFaceEmbeddings(model_name=hf_model, model_kwargs={"device": hf_device})
    else:
        # Otherwise use the configured embedding (Google GenAI) if provided,
        # else fall back to the HuggingFace default.
        if embedding_to_use:
            embeddings = GoogleGenerativeAIEmbeddings(model=embedding_to_use)
        else:
            embeddings = HuggingFaceEmbeddings(model_name=hf_model, model_kwargs={"device": hf_device})

    vector_store = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
except Exception as ei:    
    print(f"🔥 Error initializing models or vector store: {ei}")
    llm = None
    embeddings = None
    vector_store = None
    retriever = None

# --- Google Sheets Authentication ---
try:
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    spreadsheet = gc.open_by_key(GSHEET_ID)
    print("✅ Successfully connected to Google Sheets.")
except Exception as e:
    print(f"🔥 Failed to connect to Google Sheets: {e}")
    spreadsheet = None


# --- 2. Define the Agent State and Tools ---

class AgentState(TypedDict):
    query: str
    name: str
    email: str
    intent: str
    context: str
    response: str


def rag_search(state: AgentState) -> AgentState:
    """Performs a RAG search on the vector database."""
    print("---TOOL: RAG Search---")
    query = state["query"]
    docs = retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in docs])
    return {**state, "context": context}


def google_sheets_read(state: AgentState) -> AgentState:
    """Reads upcoming meetup info from Google Sheets."""
    print("---TOOL: Google Sheets Read---")
    if not spreadsheet:
        return {**state, "context": "Error: Could not connect to Google Sheets."}
    try:
        worksheet = spreadsheet.worksheet("Upcoming")
        df = pd.DataFrame(worksheet.get_all_records())
        if df.empty:
            context = "No upcoming meetups are scheduled at the moment."
        else:
            context = "Here is the information for the next meetup:\n\n" + df.to_string(index=False)
        return {**state, "context": context}
    except Exception as e:
        return {**state, "context": f"Error reading from Google Sheets: {e}"}


def google_sheets_write(state: AgentState) -> AgentState:
    """Writes contribution interest to Google Sheets."""
    print("---TOOL: Google Sheets Write---")
    if not spreadsheet:
        return {**state, "response": "Sorry, I couldn't save your interest due to a connection issue."}
    try:
        worksheet = spreadsheet.worksheet("Contributions")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, state["name"], state["email"], state["query"]]
        worksheet.append_row(row)
        response = "Thanks for your interest! We've received your submission and will contact you at the email provided."
        return {**state, "response": response}
    except Exception as e:
        return {**state, "response": f"Sorry, there was an error saving your interest: {e}"}


# --- 3. Define the LangGraph Nodes ---

def classify_intent_node(state: AgentState) -> AgentState:
    """Classifies the user's intent."""
    print("---NODE: Classify Intent---")
    prompt = ChatPromptTemplate.from_template(
        """Given the user query, classify its intent. The possible intents are:
        1. `PAST_MEETUP_QUERY`: The user is asking a question about a past topic, speaker, or tool.
        2. `UPCOMING_MEETUP_QUERY`: The user is asking about the next or an upcoming meetup.
        3. `CONTRIBUTION_INTEREST`: The user is expressing interest in speaking, presenting, or contributing.

        User Query: {query}
        
        Intent:"""
    )
    chain = prompt | llm | StrOutputParser()
    intent = chain.invoke({"query": state["query"]})
    print(f"   -> Intent: {intent}")
    return {**state, "intent": intent}


def tool_execution_node(state: AgentState) -> AgentState:
    """Routes to the correct tool based on intent."""
    print("---NODE: Execute Tool---")
    try:
        intent = state["intent"]
        if "PAST_MEETUP_QUERY" in intent:
            return rag_search(state)
        elif "UPCOMING_MEETUP_QUERY" in intent:
            return google_sheets_read(state)
        # Default or fallback to contribution if intent is unclear but seems like an offer
        elif "CONTRIBUTION_INTEREST" in intent:
            return google_sheets_write(state)
        else: # Fallback for unclear intents
            print("   -> Fallback to RAG search for unclear intent.")
            return rag_search(state)
    except Exception as e:
        print(f"Error during tool execution: {e}")
        return {**state, "response": "Sorry, something went wrong while processing your request."} 


def generate_response_node(state: AgentState) -> AgentState:
    """Generates a final response to the user."""
    print("---NODE: Generate Response---")
    response = ""
    try:
        # If a direct response was set by a tool (e.g., sheets_write), use it.
        if state.get("response"):
            return state

        prompt = ChatPromptTemplate.from_template(
            """You are the CNJDS Meetup Knowledge Agent. Based on the following context, answer the user's query.
            If the context is empty or doesn't contain the answer, state that you couldn't find the information.
            
            Context:
            {context}
            
            Query:
            {query}
            
            Answer:"""
        )
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"context": state["context"], "query": state["query"]})
    except Exception as e:
        print(f"Error during response generation: {e}")
        response = "Sorry, something went wrong while generating the response."
    return {**state, "response": response}


# --- 4. Build and Compile the LangGraph ---


print("Building the graph...")
graph_builder = StateGraph(AgentState)

graph_builder.add_node("classify_intent", classify_intent_node)
graph_builder.add_node("execute_tool", tool_execution_node)
graph_builder.add_node("generate_response", generate_response_node)

graph_builder.set_entry_point("classify_intent")

# Conditional routing after tool execution
def should_generate_response(state: AgentState):
    # If the tool itself generated a final response (like the contribution confirmation), end the graph.
    if state.get("response"):
        return END
    # Otherwise, proceed to the generation step.
    return "generate_response"

graph_builder.add_edge("classify_intent", "execute_tool")
graph_builder.add_conditional_edges(
    "execute_tool",
    should_generate_response,
    {
        "generate_response": "generate_response",
        END: END
    }
)
graph_builder.add_edge("generate_response", END)

agent = graph_builder.compile()
print("✅ Graph compiled successfully.")


# --- 5. Define the Gradio Interface and Logic ---

def respond(message: str, chat_history: List, name: str, email: str) -> str:
    """
    The main callback function for the Gradio ChatInterface.
    """
    if not name or not email:
        return "Please provide your name and email address before asking a question."

    # Initialize all keys the nodes might expect to avoid KeyErrors.
    initial_state = {
        "query": message,
        "name": name,
        "email": email,
        "intent": "",
        "context": "",
        "response": "",
    }

    try:
        final_state = None
        # Stream the graph execution to see the steps
        for step in agent.stream(initial_state):
            # The last state in the stream is the final state
            final_state = step

        # If nothing produced a final state, return a helpful fallback message
        if final_state and END in final_state:
             return final_state[END].get("response", "Sorry, I could not find a response.")

        return "Sorry, something went wrong and I could not get a response."

    except Exception as e:
        print(f"Error during graph execution: {e}")
        return "Sorry, something went wrong while processing your request."


# Build the Gradio UI
with gr.Blocks(theme=gr.themes.Soft(), title="CNJDS Meetup Knowledge Agent") as demo:
    gr.Markdown("# 🤖 CNJDS Meetup Knowledge Agent")
    gr.Markdown("Ask me about past meetups, see what's coming up, or express interest in contributing!")
    
    with gr.Row():
        name_input = gr.Textbox(label="Your Name", placeholder="Enter your name...")
        email_input = gr.Textbox(label="Your Email", placeholder="Enter your email...")
        
    
    gr.ChatInterface(
        fn=respond,
        additional_inputs=[name_input, email_input],
        examples=[
            ["What can you tell me about RAG search?"],
            ["Who presented on Large Language Models?"],
            ["What is the next meetup?"],
            ["I would like to present on vector databases next month."]
        ],
        chatbot=gr.Chatbot(height=500),
        type="messages",
        textbox=gr.Textbox(placeholder="Ask your question here...", container=False, scale=7),
    )

if __name__ == "__main__":
    print("🚀 Launching Gradio App...")
    demo.launch()