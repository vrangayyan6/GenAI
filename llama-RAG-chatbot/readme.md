# Llama 3.2 RAG Chatbot with Streamlit

![Llama 3.2 RAG Chatbot UI](https://github.com/vrangayyan6/GenAI/blob/main/llama-RAG-chatbot/Llama%20RAG%20chatbot.png)

A simple yet powerful chatbot application built with Streamlit that leverages the Llama 3.2 model via Ollama. It uses Retrieval-Augmented Generation (RAG) with ChromaDB to answer questions based on a custom knowledge base of PDF documents.

## Features

- **Interactive Chat Interface**: A clean and user-friendly web interface powered by Streamlit.
- **Local LLM**: Utilizes the Llama 3.2 model running locally via Ollama, ensuring privacy and control.
- **Retrieval-Augmented Generation (RAG)**: Provides context-aware answers by retrieving relevant information from your documents before generating a response.
- **Vector Storage**: Uses ChromaDB for efficient vector storage and similarity search.
- **Custom Knowledge Base**: Easily ingest your own PDF documents to create a personalized chatbot.

## Tech Stack

- Python 3.8+
- Streamlit
- LangChain
- Ollama
- ChromaDB
- Llama 3.2

## Prerequisites

Before you begin, ensure you have [Ollama](https://ollama.com/) installed and running on your system.

## Setup and Installation

Follow these steps to get the application running on your local machine.

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  **Create and activate a virtual environment:**
    This keeps your project dependencies isolated.
    ```bash
    python -m venv llama-venv
    ```
    -   **On Windows:**
        ```bash
        .\llama-venv\Scripts\activate
        ```
    -   **On macOS/Linux:**
        ```bash
        source llama-venv/bin/activate
        ```

3.  **Install Ollama:**
    If you haven't already, install Ollama by following the instructions on the [official website](https://ollama.com/). For Linux or macOS, you can use:
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```

4.  **Pull the Llama 3.2 model:**
    Run the following command in your terminal to download the required model. The application is configured to use `llama3.2:3b` or `llama3.2:1b`.
    ```bash
    ollama run llama3.2:3b  # or llama3.2:1b
    ```
    This command will also start the Ollama server if it's not already running.

5.  **Install Python dependencies:**
    Install all the necessary libraries from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Add Your Documents:**
    Place your PDF files inside the `docs/` directory at the root of the project. If this directory doesn't exist, please create it.

2.  **Ingest the Documents:**
    Run the ingestion script to process your documents and build the ChromaDB vector store. This step is only required once, or whenever you add, remove, or change the documents in the `docs/` directory.
    ```bash
    python -m src.util.ingest
    ```
    This will create a `chroma_db/` directory containing the vector embeddings.

3.  **Run the Streamlit Application:**
    Start the chatbot application with the following command:
    ```bash
    streamlit run app.py
    ```
    Your default web browser should open a new tab with the chatbot interface. You can now start asking questions about your documents!

## Project Structure

```
.
├── app.py                  # Main Streamlit application file
├── chroma_db/              # Directory for the ChromaDB vector store (created by ingest.py)
├── docs/                   # Place your PDF documents here
├── requirements.txt        # Python dependencies
├── src/
│   ├── chatbot/
│   │   └── __init__.py     # Contains the Chatbot class and RAG chain logic
│   └── util/
│       └── ingest.py       # Script for ingesting documents into ChromaDB
└── README.md               # This file
```

## Configuration

-   **Model Parameters**: The LLM model (`llama3.2:3b` or `llama3.2:1b`), temperature, and other generation parameters can be configured in `src/chatbot/__init__.py`.
-   **Text Splitting**: Chunk size and overlap for document processing can be adjusted in `src/util/ingest.py`.
-   **Prompt Template**: The RAG prompt template can be modified in `src/chatbot/__init__.py` to change the chatbot's behavior and response style.
