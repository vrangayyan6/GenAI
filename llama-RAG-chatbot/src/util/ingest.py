"""Execute the ingestion script from your project's root directory. 
This only needs to be done once, or whenever you add/change your documents.

python -m src.util.ingest

"""

import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma

# Define paths relative to the project root to ensure they work regardless of execution context.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOCS_PATH = os.path.join(PROJECT_ROOT, "docs")
CHROMA_PATH = os.path.join(PROJECT_ROOT, "chroma_db")

def ingest_documents():
    """
    Ingests PDF documents from the 'docs' directory into a ChromaDB vector store.
    """
    print(f"Loading documents from {DOCS_PATH}...")
    if not os.path.exists(DOCS_PATH) or not os.listdir(DOCS_PATH):
        print(f"No documents found in {DOCS_PATH}. Please create the 'docs' directory and add your PDF files.")
        return

    document_loader = PyPDFDirectoryLoader(DOCS_PATH)
    documents = document_loader.load()
    if not documents:
        print("No documents were loaded. Check your PDF files. Exiting.")
        return
    print(f"Loaded {len(documents)} document(s).")

    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    if os.path.exists(CHROMA_PATH):
        print(f"Clearing existing database at {CHROMA_PATH}...")
        shutil.rmtree(CHROMA_PATH)

    print("Creating new ChromaDB vector store and embedding documents...")
    embeddings = OllamaEmbeddings(model="llama3.2:1b", show_progress=True)
    db = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=CHROMA_PATH)
    print(f"Successfully created vector store with {db._collection.count()} documents, persisted at: {CHROMA_PATH}")

if __name__ == "__main__":
    ingest_documents()
