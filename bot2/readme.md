# CNJDS Meetup Knowledge Agent

Link to Gemini conversation refining requirements, design and code [https://g.co/gemini/share/f0bb3fc2d423](https://g.co/gemini/share/f0bb3fc2d423) 

---

## **1.0 Project Overview & Goals**

The **CNJDS Meetup Knowledge Agent** will be an AI-powered web application designed to serve the Central New Jersey Data Science (CNJDS) community. The primary goal is to provide a centralized, interactive, and user-friendly interface for members to access information about past and upcoming meetups. A secondary goal is to streamline the process for members to express interest in contributing to future events.

* **Project Vision:** To create an intelligent, self-service information hub that enhances member engagement and reduces the administrative burden on meetup organizers.  
* **Key Stakeholders:** Meetup Members (End Users), Meetup Organizers (Administrators).

---

## **2.0 User Roles**

* **User / Meetup Member:** An individual visiting the web page to query information or express interest in presenting.  
* **Administrator:** A CNJDS organizer responsible for maintaining the data sources (e.g., uploading presentation PDFs and updating the Google Sheet for upcoming events).

---

## **3.0 Functional Requirements**

### **FR-1: User Interface (UI) & Data Capture**

* **FR-1.1:** The application shall present a single web page with a clear headline (e.g., "CNJDS Meetup Knowledge Agent") and a brief, static welcome message explaining the agent's purpose.  
* **FR-1.2:** The UI must contain input fields for the **User's Name** and **User's Email Address**. These fields must be captured before or along with the user's first interaction.  
* **FR-1.3:** The UI shall feature a main chat/query interface where users can submit their requests in natural language.  
* **FR-1.4:** The UI must present three clear, clickable options or suggested prompts to guide the user:  
  1. "Search Past Meetups"  
  2. "See Upcoming Meetups"  
  3. "I want to contribute"

### **FR-2: Use Case 1 \- Querying Past Meetups**

* **FR-2.1:** The system shall use a Retrieval-Augmented Generation (RAG) approach, querying a vector database created from past meetup documents (e.g., PDFs of presentations) stored in a designated Google Drive folder.  
* **FR-2.2:** The system must be able to parse and respond to user queries based on the following categories:  
  * **Topic:** e.g., "What do you know about RAG search?"  
  * **Speaker:** e.g., "Show me presentations by Suresh."  
  * **Tools/Technology:** e.g., "Find meetups that mentioned Hugging Face or LangChain."  
  * **Date:** e.g., "What was the topic in March 2025?"  
* **FR-2.3 (Success Output):** When relevant information is found, the system shall return a concise summary including all available fields: **Title**, **Synopsis/Description**, **Month/Year**, **Speaker**, and a **Document Link** to the source material in Google Drive.  
* **FR-2.4 (Failure Output):** If the vector database search yields no relevant results, the system must respond with a clear and helpful message, such as: "I could not find any information related to your query in the meetup archive. Please try rephrasing your question."

### **FR-3: Use Case 2 \- Retrieving Upcoming Meetup Information**

* **FR-3.1:** The system shall respond to explicit requests for upcoming meetup information, such as "What's the next meetup?" or "provide information on upcoming meetups."  
* **FR-3.2:** Upon receiving such a request, the system will read data directly from a dedicated "Upcoming" tab within a designated Google Sheet.  
* **FR-3.3 (Data Source):** The Google Sheet will contain the columns: Title, Synopsis/Description, Month/Year, Speaker.  
* **FR-3.4 (Success Output):** The system shall format the information from the Google Sheet into a clean, human-readable format for the user, displaying all available fields for the next scheduled event.  
* **FR-3.5 (Admin Responsibility):** The Administrator is responsible for keeping this Google Sheet tab accurate, including any updates, date changes, or cancellations.

### **FR-4: Use Case 3 \- Capturing Contribution Interest**

* **FR-4.1:** The system shall recognize user intent to contribute or present, based on inputs like "I would like to present on RAG chatbots."  
* **FR-4.2:** Upon detecting this intent, the system shall write the user's information to a dedicated "Contributions" tab in the designated Google Sheet.  
* **FR-4.3 (Data Capture):** The system will capture the **Contributor Name** and **Contributor Email** (from FR-1.2) and parse the user's message to capture the proposed **Topic** and **Details**.  
* **FR-4.4 (Confirmation Output):** After successfully writing to the Google Sheet, the system must display a confirmation message to the user: "Thanks for your interest\! We will contact you at the email address you provided."

---

## **4.0 Non-Functional Requirements (NFRs)**

* **NFR-1 (Performance):** The system should provide a response to a user query within **5-7 seconds** under normal operating conditions.  
* **NFR-2 (Usability):** The web interface must be responsive and fully functional on both desktop and modern mobile web browsers.  
* **NFR-3 (Security):** All communication between the client and the server must be encrypted via HTTPS. User email addresses should be handled as Personally Identifiable Information (PII) and not be exposed publicly.  
* **NFR-4 (Availability):** The service should strive for 99.5% uptime. A clear message should be displayed if backend services (e.g., Gemini API, Google Cloud) are temporarily unavailable.

---

## **5.0 Technical Architecture & Stack**

This section confirms the high-level technical components that will be used to build the solution.

* **LLM API:** **Google Gemini Flash API** (via a free developer account).  
* **Compute/Hosting:** **Google Cloud VM** to host the Python backend application, required packages, and the vector database.  
* **Data Storage:**  
  * **Google Drive:** To serve as the central repository for source documents (e.g., meetup PDFs) for vectorization.  
  * **Google Sheets:** To act as a simple, admin-updatable database for:  
    1. Upcoming meetup details.  
    2. A log of contribution interests.  
* **Vector Database:** A local or lightweight vector database such as **ChromaDB** or **FAISS** running on the Google Cloud VM.  
* **Agent Framework:** An agentic framework like **LangGraph** or **CrewAI** to manage the logic flow, tool selection (e.g., RAG search vs. Google Sheet lookup), and interaction with the LLM.  
* **Version Control:** A **Git repository** (e.g., on GitHub, GitLab) with a common project email address for collaborator access.  
* **Minimum Viable Product (MVP):** The initial build will focus on delivering the core functionality described in the functional requirements. Advanced features like conversation history or user authentication are out of scope for the MVP.

## Design

---

## **1.0 System Architecture (Revised)**

The architecture is now simplified into a **single, unified Python application**. Gradio will serve as both the frontend UI and the web server, eliminating the need for a separate FastAPI backend to handle API requests. This creates a more monolithic but significantly easier-to-manage system.

* **Gradio Application (on GCP VM):** This single Python process is the core of the system.  
  * It runs the web server that hosts the interactive UI.  
  * It contains all the backend logic, including the Agent Core (LangGraph), database connections, and integrations with Google services.  
* **Data Stores & External Services:** These components remain the same (Google Drive, Google Sheets, ChromaDB, Gemini API). They are now accessed directly by functions within the Gradio application script.

---

## **2.0 Component Design (Revised)**

The main change is the consolidation of the Frontend and Backend API components into one Gradio application definition.

### **2.1 UI and Application Server (Gradio)**

* **Framework:** **Gradio** will be used to create the user interface. The entire application will be defined in a single app.py script.  
* **Functionality:**  
  * A Gradio gr.Blocks interface will be built to provide a custom layout.  
  * **Input Components:**  
    * gr.Textbox(label="Your Name") to capture the user's name.  
    * gr.Textbox(label="Your Email") to capture the user's email address.  
    * A gr.ChatInterface will be the primary component for user interaction. This component natively handles the display of chat history and provides a text input box.  
  * **Core Logic Function:** A single Python function, let's call it respond(message, chat\_history, name, email), will be the central callback for the ChatInterface. This function will receive the user's inputs and execute the entire backend process.

### **2.2 Core Application Logic (Formerly Backend API)**

This component is no longer a separate API but a Python function directly invoked by the Gradio UI. The internal logic remains the same.

* **Trigger:** The respond function is triggered every time the user submits a message in the ChatInterface.  
* **Process:**  
  1. The function receives the name, email, and user message (query) from the Gradio components.  
  2. It invokes the **Agent Core (LangGraph)**, passing the query to the classify\_intent node.  
  3. The LangGraph graph executes exactly as designed previously, routing to the correct tool (RAG search, Sheets read, or Sheets write).  
  4. The final generate\_response node produces the user-facing answer.  
  5. The function returns the final string, which Gradio then automatically displays in the ChatInterface output.

### **2.3 Agent Core (Unchanged)**

The design and implementation of the LangGraph agent remain **identical**. It is a self-contained module that handles the business logic and is simply called by the respond function instead of a FastAPI endpoint handler. Its nodes and conditional logic for routing between tools are not affected by the UI framework.

### **2.4 Data Ingestion & Processing (Unchanged)**

The utility script sync\_vectordb.py for populating the ChromaDB from Google Drive remains **unchanged**. It is a separate, offline process independent of the user-facing application.

---

## **3.0 & 4.0 (Unchanged)**

Sections **3.0 Data Models & Storage** and **4.0 Security & Configuration** remain the same. The methods for storing data and managing credentials (.env file, service accounts) are not impacted by this change.

---

## **5.0 Deployment Plan (Revised)**

The deployment process is simplified.

1. **GCP VM Setup:** This remains the same (create VM, install Python, clone repo, install dependencies from requirements.txt).  
2. **Running the Application:** Instead of using Gunicorn for a FastAPI app, you will run the Gradio app directly from the terminal.  
   * python app.py  
   * Gradio's built-in web server will start, typically on port 7860. For production, the application can still be run using Gunicorn for better process management.  
3. **Firewall Configuration:** The GCP firewall rules must be updated to allow ingress traffic on the port Gradio is running on (e.g., TCP 7860).  
4. **Development Sharing:** During development, Gradio's share=True parameter can be used to generate a temporary public URL for easy testing and demos without configuring the GCP firewall.

---

## **6.0 MVP Development Plan (Revised)**

The development phases are slightly adjusted and streamlined.

1. **Phase 1: Backend & Core Logic (Unchanged):** Develop the LangGraph agent and its tools. Test the logic independently.  
2. **Phase 2: Data & Integration (Unchanged):** Implement the sync\_vectordb.py script and set up Google Sheets integration.  
3. **Phase 3: UI Implementation & Integration:**  
   * Create the app.py script.  
   * Define the Gradio Blocks layout with the name, email, and ChatInterface components.  
   * Write the respond callback function and integrate the Agent Core logic from Phase 1 into it.  
4. **Phase 4: Deployment & Testing:** Deploy the single app.py to the GCP VM, run it, and perform end-to-end testing through the Gradio web UI.

## Code

Of course. Here is the complete code for the CNJDS Meetup Knowledge Agent based on the specified Gradio design.

This solution is broken into three parts:

1. **Prerequisites & Setup:** What you need to install and configure.  
2. **Data Ingestion Script (sync\_vectordb.py):** The script to process your PDFs into a vector database.  
3. **Main Application (app.py):** The Gradio application that users will interact with.

---

## **1\. Prerequisites & Setup**

Before running the code, you must set up your environment and credentials.

### **A. Project Structure**

Create a project folder with the following structure:

/cnjds-agent/  
|-- .env  
|-- requirements.txt  
|-- service\_account.json  
|-- sync\_vectordb.py  
|-- app.py  
|-- /db/              \<-- ChromaDB will store its files here  
|-- /temp\_pdfs/       \<-- PDFs will be downloaded here temporarily

### **B. Install Dependencies**

Create a requirements.txt file with the following content:

Plaintext

\# Core libraries  
gradio  
langchain  
langgraph  
langchain-google-genai  
langchain-community

\# Data and utilities  
python-dotenv  
pandas  
gspread  
oauth2client  
google-api-python-client  
PyDrive2

\# For PDF processing and vector store  
pypdf  
chromadb

Install them using pip:

pip install \-r requirements.txt

### **C. Google Cloud & Drive/Sheets Setup**

1. **Google Cloud Project:** Create a new project in the [Google Cloud Console](https://console.cloud.google.com/).  
2. **Enable APIs:** In your project, enable the following APIs:  
   * Generative Language API (for Gemini)  
   * Google Drive API  
   * Google Sheets API  
3. **Create Service Account:**  
   * Go to IAM & Admin \> Service Accounts and create a new service account.  
   * Grant it the Editor role for simplicity during development.  
   * Create a key for this service account (JSON format) and download it. **Rename this file to service\_account.json** and place it in your project folder.  
4. **Get a Gemini API Key:** Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and create a free API key.  
5. **Share Google Drive & Sheets:**  
   * Create a Google Drive folder and get its ID from the URL. This is your GDRIVE\_FOLDER\_ID. Upload your meetup PDFs here.  
   * Create a Google Sheet and get its ID from the URL. This is your GSHEET\_ID. Create two tabs named exactly Upcoming and Contributions.  
   * **Crucially, you must share both the Drive folder and the Google Sheet with the service account's email address** (e.g., my-service-account@my-project.iam.gserviceaccount.com). Give it "Editor" access.

### **D. Environment Variables**

Create a .env file in your project folder with the following content:

Ini, TOML

\# Your Gemini API Key from Google AI Studio  
GOOGLE\_API\_KEY\="YOUR\_GEMINI\_API\_KEY"

\# The ID of the Google Drive folder containing your PDFs  
GDRIVE\_FOLDER\_ID\="YOUR\_GOOGLE\_DRIVE\_FOLDER\_ID"

\# The ID of the Google Sheet for upcoming meetups and contributions  
GSHEET\_ID\="YOUR\_GOOGLE\_SHEET\_ID"

---

## **2\. Data Ingestion Script (sync\_vectordb.py)**

This script connects to your Google Drive, downloads the PDFs, and populates the local ChromaDB vector store. Run this script once before you start the main application, and re-run it whenever you add new PDFs to the Drive folder.

\# sync\_vectordb.py

import os  
from dotenv import load\_dotenv  
from pydrive2.auth import GoogleAuth  
from pydrive2.drive import GoogleDrive  
from langchain\_community.document\_loaders import PyPDFLoader  
from langchain.text\_splitter import RecursiveCharacterTextSplitter  
from langchain\_chroma import Chroma  \# \<-- CORRECTED IMPORT  
from langchain\_google\_genai import GoogleGenerativeAIEmbeddings

\# Load environment variables from .env file  
load\_dotenv()

\# \--- Configuration \---  
GDRIVE\_FOLDER\_ID \= os.getenv("GDRIVE\_FOLDER\_ID")  
DB\_DIR \= os.path.join(os.path.dirname(\_\_file\_\_), "db")  
PDF\_TEMP\_DIR \= os.path.join(os.path.dirname(\_\_file\_\_), "temp\_pdfs")  
os.makedirs(PDF\_TEMP\_DIR, exist\_ok=True)  
os.makedirs(DB\_DIR, exist\_ok=True)

def authenticate\_gdrive():  
    """Authenticate with Google Drive using a service account."""  
    \# \--- THIS FUNCTION IS NOW CORRECTED \---  
    settings \= {  
        "client\_config\_backend": "service",  
        "service\_config": {  
            "client\_secrets\_path": "service\_account.json"  
        }  
    }  
    gauth \= GoogleAuth(settings=settings)  
    gauth.ServiceAuth()  
    drive \= GoogleDrive(gauth)  
    return drive

def sync\_vector\_db():  
    """  
    Synchronizes the vector database with PDFs from a Google Drive folder.  
    """  
    print("🚀 Starting vector database synchronization...")

    \# \--- 1\. Initialize Embeddings and Vector Store \---  
    print("Initializing embeddings model and vector store...")  
    embeddings \= GoogleGenerativeAIEmbeddings(model="models/embedding-001")  
    vector\_store \= Chroma(  
        persist\_directory=DB\_DIR,  
        embedding\_function=embeddings  
    )  
      
    \# \--- 2\. Authenticate and List Files from Google Drive \---  
    print(f"Connecting to Google Drive Folder ID: {GDRIVE\_FOLDER\_ID}...")  
    drive \= authenticate\_gdrive()  
    query \= f"'{GDRIVE\_FOLDER\_ID}' in parents and trashed=false and mimeType='application/pdf'"  
    file\_list \= drive.ListFile({'q': query}).GetList()  
      
    if not file\_list:  
        print("No PDFs found in the specified Google Drive folder. Exiting.")  
        return

    print(f"Found {len(file\_list)} PDF(s) in Google Drive.")

    \# \--- 3\. Process each PDF \---  
    processed\_files \= 0  
    for file in file\_list:  
        print(f"\\nProcessing file: {file\['title'\]}...")  
        file\_path \= os.path.join(PDF\_TEMP\_DIR, file\['title'\])  
          
        \# Download the file  
        file.GetContentFile(file\_path)  
          
        \# Load and split the PDF  
        loader \= PyPDFLoader(file\_path)  
        documents \= loader.load()  
        text\_splitter \= RecursiveCharacterTextSplitter(chunk\_size=1000, chunk\_overlap=150)  
        docs \= text\_splitter.split\_documents(documents)  
          
        \# Add documents to the vector store  
        vector\_store.add\_documents(docs)  
        print(f"✅ Added {len(docs)} document chunks for '{file\['title'\]}' to the vector store.")  
          
        \# Clean up the downloaded file  
        os.remove(file\_path)  
        processed\_files \+= 1

    print(f"\\n✨ Synchronization complete\! Processed {processed\_files} PDF(s).")  
    print(f"Vector database is persisted at: {DB\_DIR}")

if \_\_name\_\_ \== "\_\_main\_\_":  
    sync\_vector\_db()

---

## **3\. Main Application (app.py)**

This is the main application file. It contains the Gradio UI, the LangGraph agent, and all the tools for interacting with the vector store and Google Sheets.

\# app.py

import os  
import gspread  
import pandas as pd  
from datetime import datetime  
from typing import TypedDict, List  
from dotenv import load\_dotenv

import gradio as gr  
from langchain\_chroma import Chroma  \# \<-- CORRECTED IMPORT  
from langchain\_core.messages import BaseMessage, HumanMessage  
from langchain\_google\_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings  
from langchain\_core.output\_parsers import StrOutputParser  
from langchain\_core.prompts import ChatPromptTemplate  
from langgraph.graph import StateGraph, END

\# \--- 1\. Load Environment Variables and Initial Setup \---  
load\_dotenv()

\# \--- Configuration \---  
DB\_DIR \= os.path.join(os.path.dirname(\_\_file\_\_), "db")  
GSHEET\_ID \= os.getenv("GSHEET\_ID")  
SERVICE\_ACCOUNT\_FILE \= 'service\_account.json'

\# \--- Initialize models and vector store \---  
print("Initializing models and vector store...")  
llm \= ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)  
embeddings \= GoogleGenerativeAIEmbeddings(model="models/embedding-001")  
vector\_store \= Chroma(persist\_directory=DB\_DIR, embedding\_function=embeddings)  
retriever \= vector\_store.as\_retriever(search\_kwargs={"k": 5})

\# \--- Google Sheets Authentication \---  
try:  
    gc \= gspread.service\_account(filename=SERVICE\_ACCOUNT\_FILE)  
    spreadsheet \= gc.open\_by\_key(GSHEET\_ID)  
    print("✅ Successfully connected to Google Sheets.")  
except Exception as e:  
    print(f"🔥 Failed to connect to Google Sheets: {e}")  
    spreadsheet \= None

\# \--- 2\. Define the Agent State and Tools \---

class AgentState(TypedDict):  
    query: str  
    name: str  
    email: str  
    intent: str  
    context: str  
    response: str

def rag\_search(state: AgentState) \-\> AgentState:  
    """Performs a RAG search on the vector database."""  
    print("---TOOL: RAG Search---")  
    query \= state\["query"\]  
    docs \= retriever.invoke(query)  
    context \= "\\n\\n".join(\[doc.page\_content for doc in docs\])  
    return {\*\*state, "context": context}

def google\_sheets\_read(state: AgentState) \-\> AgentState:  
    """Reads upcoming meetup info from Google Sheets."""  
    print("---TOOL: Google Sheets Read---")  
    if not spreadsheet:  
        return {\*\*state, "context": "Error: Could not connect to Google Sheets."}  
    try:  
        worksheet \= spreadsheet.worksheet("Upcoming")  
        df \= pd.DataFrame(worksheet.get\_all\_records())  
        if df.empty:  
            context \= "No upcoming meetups are scheduled at the moment."  
        else:  
            context \= "Here is the information for the next meetup:\\n\\n" \+ df.to\_string(index=False)  
        return {\*\*state, "context": context}  
    except Exception as e:  
        return {\*\*state, "context": f"Error reading from Google Sheets: {e}"}

def google\_sheets\_write(state: AgentState) \-\> AgentState:  
    """Writes contribution interest to Google Sheets."""  
    print("---TOOL: Google Sheets Write---")  
    if not spreadsheet:  
        return {\*\*state, "response": "Sorry, I couldn't save your interest due to a connection issue."}  
    try:  
        worksheet \= spreadsheet.worksheet("Contributions")  
        timestamp \= datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
        \# Extract the topic from the query for a cleaner sheet entry  
        topic\_prompt \= ChatPromptTemplate.from\_template("Extract the presentation topic from this user message: {query}. Just return the topic itself.")  
        topic\_chain \= topic\_prompt | llm | StrOutputParser()  
        topic \= topic\_chain.invoke({"query": state\["query"\]})  
          
        row \= \[timestamp, state\["name"\], state\["email"\], topic, state\["query"\]\]  
        worksheet.append\_row(row)  
        response \= "Thanks for your interest\! We've received your submission and will contact you at the email provided."  
        return {\*\*state, "response": response}  
    except Exception as e:  
        return {\*\*state, "response": f"Sorry, there was an error saving your interest: {e}"}

\# \--- 3\. Define the LangGraph Nodes \---

def classify\_intent\_node(state: AgentState) \-\> AgentState:  
    """Classifies the user's intent."""  
    print("---NODE: Classify Intent---")  
    prompt \= ChatPromptTemplate.from\_template(  
        """Given the user query, classify its intent. The possible intents are:  
        1\. \`PAST\_MEETUP\_QUERY\`: The user is asking a question about a past topic, speaker, or tool. This includes "who presented on X", "tell me about Y", etc.  
        2\. \`UPCOMING\_MEETUP\_QUERY\`: The user is asking about the next or an upcoming meetup. This includes "what's next", "upcoming events", etc.  
        3\. \`CONTRIBUTION\_INTEREST\`: The user is expressing interest in speaking, presenting, or contributing. This includes "I want to present", "I can talk about Z", etc.  
        4\. \`GREETING\_OR\_THANKS\`: The user is saying hello, thanks, or having a simple conversational exchange.  
          
        User Query: {query}  
          
        Intent:"""  
    )  
    chain \= prompt | llm | StrOutputParser()  
    intent \= chain.invoke({"query": state\["query"\]})  
    print(f"   \-\> Intent: {intent}")  
    return {\*\*state, "intent": intent}  
      
def simple\_response\_node(state: AgentState) \-\> AgentState:  
    """Handles simple conversational turns like greetings."""  
    print("---NODE: Simple Response---")  
    return {\*\*state, "response": "You're welcome\! How else can I help you today?"}

def tool\_execution\_node(state: AgentState) \-\> AgentState:  
    """Routes to the correct tool based on intent."""  
    print("---NODE: Execute Tool---")  
    intent \= state\["intent"\]  
    if "PAST\_MEETUP\_QUERY" in intent:  
        return rag\_search(state)  
    elif "UPCOMING\_MEETUP\_QUERY" in intent:  
        return google\_sheets\_read(state)  
    elif "CONTRIBUTION\_INTEREST" in intent:  
        return google\_sheets\_write(state)  
    elif "GREETING\_OR\_THANKS" in intent:  
         \# This intent doesn't need a tool, it has a direct response.  
         \# We will handle this in the routing.  
        return state  
    else: \# Fallback for unclear intents  
        print("   \-\> Fallback to RAG search for unclear intent.")  
        return rag\_search(state)

def generate\_response\_node(state: AgentState) \-\> AgentState:  
    """Generates a final response to the user."""  
    print("---NODE: Generate Response---")  
    \# If a direct response was set by a tool (e.g., sheets\_write), use it.  
    if state.get("response"):  
        return state

    prompt \= ChatPromptTemplate.from\_template(  
        """You are the CNJDS Meetup Knowledge Agent. You are friendly and helpful. Based on the following context, answer the user's query.  
        If the context is empty or doesn't contain the answer, state that you couldn't find specific information in the meetup archives.  
          
        Context:  
        {context}  
          
        Query:  
        {query}  
          
        Answer:"""  
    )  
    chain \= prompt | llm | StrOutputParser()  
    response \= chain.invoke({"context": state\["context"\], "query": state\["query"\]})  
    return {\*\*state, "response": response}

\# \--- 4\. Build and Compile the LangGraph \---

print("Building the graph...")  
graph\_builder \= StateGraph(AgentState)

graph\_builder.add\_node("classify\_intent", classify\_intent\_node)  
graph\_builder.add\_node("execute\_tool", tool\_execution\_node)  
graph\_builder.add\_node("generate\_response", generate\_response\_node)  
graph\_builder.add\_node("simple\_response", simple\_response\_node)

graph\_builder.set\_entry\_point("classify\_intent")

\# Conditional routing after classification  
def route\_after\_classification(state: AgentState):  
    intent \= state\["intent"\]  
    if "GREETING\_OR\_THANKS" in intent:  
        return "simple\_response"  
    else:  
        return "execute\_tool"

graph\_builder.add\_conditional\_edges(  
    "classify\_intent",  
    route\_after\_classification,  
    {  
        "simple\_response": "simple\_response",  
        "execute\_tool": "execute\_tool",  
    }  
)

\# Conditional routing after tool execution  
def should\_generate\_response(state: AgentState):  
    \# If the tool itself generated a final response (like the contribution confirmation), end the graph.  
    if state.get("response"):  
        return END  
    \# Otherwise, proceed to the generation step.  
    return "generate\_response"

graph\_builder.add\_conditional\_edges(  
    "execute\_tool",  
    should\_generate\_response,  
    {  
        "generate\_response": "generate\_response",  
        END: END  
    }  
)  
graph\_builder.add\_edge("generate\_response", END)  
graph\_builder.add\_edge("simple\_response", END)

agent \= graph\_builder.compile()  
print("✅ Graph compiled successfully.")

\# \--- 5\. Define the Gradio Interface and Logic \---

def respond(message: str, chat\_history: List, name: str, email: str) \-\> str:  
    """  
    The main callback function for the Gradio ChatInterface.  
    """  
    if not name or not email:  
        return "Please provide your name and email address before asking a question."

    initial\_state \= {"query": message, "name": name, "email": email}  
      
    final\_state \= agent.invoke(initial\_state)

    return final\_state.get("response", "Sorry, something went wrong.")

\# Build the Gradio UI  
with gr.Blocks(theme=gr.themes.Soft(), title="CNJDS Meetup Knowledge Agent") as demo:  
    gr.Markdown("\# 🤖 CNJDS Meetup Knowledge Agent")  
    gr.Markdown("Ask me about past meetups, see what's coming up, or express interest in contributing\!")  
      
    with gr.Row():  
        name\_input \= gr.Textbox(label="Your Name", placeholder="Enter your name...")  
        email\_input \= gr.Textbox(label="Your Email", placeholder="Enter your email...")  
          
    gr.ChatInterface(  
        fn=respond,  
        additional\_inputs=\[name\_input, email\_input\],  
        examples=\[  
            \["What can you tell me about RAG search?"\],  
            \["Who presented on Large Language Models?"\],  
            \["What is the next meetup?"\],  
            \["I would like to present on vector databases next month."\]  
        \],  
        chatbot=gr.Chatbot(height=500, type='messages'),  
        textbox=gr.Textbox(placeholder="Ask your question here...", container=False, scale=7),  
        \# clear\_btn="Clear Chat", \# \<-- REMOVED THIS LINE  
    )

if \_\_name\_\_ \== "\_\_main\_\_":  
    print("🚀 Launching Gradio App...")  
    demo.launch()

---

## **4\. How to Run**

1. **Complete Setup:** Make sure you've completed all the steps in the "Prerequisites & Setup" section.  
2. **Run the Sync Script:** Open your terminal in the project directory and run the data ingestion script first.

   Bash  
   python sync\_vectordb.py

3. This will create the /db and /temp\_pdfs folders and populate your vector store. You only need to do this when you add new PDFs.  
4. **Run the Main App:** Once the sync is complete, run the main application.

   Bash  
   python app.py

5. **Access the UI:** The terminal will output a local URL, usually http://127.0.0.1:7860. Open this URL in your web browser to interact with the agent.

