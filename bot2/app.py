# app.py

import os
import gspread
import pandas as pd
from datetime import datetime
from typing import TypedDict, Annotated, List
from dotenv import load_dotenv

import gradio as gr
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

# --- 1. Load Environment Variables and Initial Setup ---
load_dotenv()

# --- Configuration ---
DB_DIR = os.path.join(os.path.dirname(__file__), "db")
GSHEET_ID = os.getenv("GSHEET_ID")
SERVICE_ACCOUNT_FILE = 'service_account.json'

# --- Initialize models and vector store ---
print("Initializing models and vector store...")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0.7)
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 5})

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
        # Extract the topic from the query for a cleaner sheet entry
        topic_prompt = ChatPromptTemplate.from_template("Extract the presentation topic from this user message: {query}. Just return the topic itself.")
        topic_chain = topic_prompt | llm | StrOutputParser()
        topic = topic_chain.invoke({"query": state["query"]})
        
        row = [timestamp, state["name"], state["email"], topic, state["query"]]
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
        3. `CONTRIBUTION_INTEREST`: The user is expressing interest in speaking, presenting, or contributing. This includes "I want to present", "I can talk about Z", etc.
        4. `GREETING_OR_THANKS`: The user is saying hello, thanks, or having a simple conversational exchange.

        User Query: {query}
        
        Intent:"""
    )
    chain = prompt | llm | StrOutputParser()
    intent = chain.invoke({"query": state["query"]})
    print(f"   -> Intent: {intent}")
    return {**state, "intent": intent}

def simple_response_node(state: AgentState) -> AgentState:
    """Handles simple conversational turns like greetings."""
    print("---NODE: Simple Response---")
    # This can be made more sophisticated, but for now, a simple canned response works.
    if "thank" in state["query"].lower():
        response = "You're welcome! How else can I help you today?"
    else:
        response = "Hello! How can I help you with the CNJDS meetups?"
    return {**state, "response": response}

def tool_execution_node(state: AgentState) -> AgentState:
    """Routes to the correct tool based on intent."""
    print("---NODE: Execute Tool---")
    intent = state["intent"]
    if "PAST_MEETUP_QUERY" in intent:
        return rag_search(state)
    elif "UPCOMING_MEETUP_QUERY" in intent:
        return google_sheets_read(state)
    elif "CONTRIBUTION_INTEREST" in intent:
        return google_sheets_write(state)
    elif "GREETING_OR_THANKS" in intent:
        # This intent doesn't need a tool, it has a direct response.
        return state # Pass through, will be routed to simple_response_node
    else: # Fallback for unclear intents
        print("   -> Fallback to RAG search for unclear intent.")
        return rag_search(state)

def generate_response_node(state: AgentState) -> AgentState:
    """Generates a final response to the user."""
    print("---NODE: Generate Response---")
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
    return {**state, "response": response}

# --- 4. Build and Compile the LangGraph ---

print("Building the graph...")
graph_builder = StateGraph(AgentState)

graph_builder.add_node("classify_intent", classify_intent_node)
graph_builder.add_node("execute_tool", tool_execution_node)
graph_builder.add_node("generate_response", generate_response_node)
graph_builder.add_node("simple_response", simple_response_node)

graph_builder.set_entry_point("classify_intent")

# Conditional routing after classification
def route_after_classification(state: AgentState):
    intent = state["intent"]
    if "GREETING_OR_THANKS" in intent:
        return "simple_response"
    else:
        return "execute_tool"

graph_builder.add_conditional_edges(
    "classify_intent",
    route_after_classification,
)

# Conditional routing after tool execution
def should_generate_response(state: AgentState):
    # If the tool itself generated a final response (like the contribution confirmation), end the graph.
    if state.get("response"):
        return END
    # Otherwise, proceed to the generation step.
    return "generate_response"

graph_builder.add_conditional_edges(
    "execute_tool",
    should_generate_response,
    {
        "generate_response": "generate_response",
        END: END
    }
)
graph_builder.add_edge("generate_response", END)
graph_builder.add_edge("simple_response", END)

agent = graph_builder.compile()
print("✅ Graph compiled successfully.")

# --- 5. Define the Gradio Interface and Logic ---

def respond(message: str, chat_history: List, name: str, email: str) -> str:
    """
    The main callback function for the Gradio ChatInterface.
    """
    if not name or not email:
        return "Please provide your name and email address before asking a question."

    initial_state = {"query": message, "name": name, "email": email}

    final_state = None
    for step in agent.stream(initial_state):
        # The last state in the stream is the final state
        final_state = step
    
    return final_state.get("response", "Sorry, something went wrong.")


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
        chatbot=gr.Chatbot(height=500, type='messages'), # <-- ADDED type='messages'
        textbox=gr.Textbox(placeholder="Ask your question here...", container=False, scale=7),
        # clear_btn="Clear Chat", # <-- REMOVED THIS LINE
    )

if __name__ == "__main__":
    print("🚀 Launching Gradio App...")
    demo.launch()