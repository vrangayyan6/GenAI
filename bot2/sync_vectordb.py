# sync_vectordb.py

import os
from dotenv import load_dotenv
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")
DB_DIR = os.path.join(os.path.dirname(__file__), "db")
PDF_TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp_pdfs")
os.makedirs(PDF_TEMP_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

def authenticate_gdrive():
    """Authenticate with Google Drive using a service account."""
    settings = {
        "client_config_backend": "service",
        "service_config": {
            "client_json_file_path": "service_account.json"
        }
    }
    gauth = GoogleAuth(settings=settings)
    gauth.ServiceAuth()  # Authenticate with the settings provided.
    drive = GoogleDrive(gauth)
    return drive

def sync_vector_db():
    """
    Synchronizes the vector database with PDFs from a Google Drive folder.
    """
    print("🚀 Starting vector database synchronization...")

    # --- 1. Initialize Embeddings and Vector Store ---
    print("Initializing embeddings model and vector store...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embeddings
    )
    
    # --- 2. Authenticate and List Files from Google Drive ---
    print(f"Connecting to Google Drive Folder ID: {GDRIVE_FOLDER_ID}...")
    drive = authenticate_gdrive()
    query = f"'{GDRIVE_FOLDER_ID}' in parents and trashed=false and mimeType='application/pdf'"
    file_list = drive.ListFile({'q': query}).GetList()
    
    if not file_list:
        print("No PDFs found in the specified Google Drive folder. Exiting.")
        return

    print(f"Found {len(file_list)} PDF(s) in Google Drive.")

    # --- 3. Process each PDF ---
    processed_files = 0
    for file in file_list:
        print(f"\nProcessing file: {file['title']}...")
        file_path = os.path.join(PDF_TEMP_DIR, file['title'])
        
        # Download the file
        file.GetContentFile(file_path)
        
        # Load and split the PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        docs = text_splitter.split_documents(documents)
        
        # Add documents to the vector store
        # This will create embeddings and store them.
        vector_store.add_documents(docs)
        print(f"✅ Added {len(docs)} document chunks for '{file['title']}' to the vector store.")
        
        # Clean up the downloaded file
        os.remove(file_path)
        processed_files += 1

    print(f"\n✨ Synchronization complete! Processed {processed_files} PDF(s).")
    print(f"Vector database is persisted at: {DB_DIR}")

if __name__ == "__main__":
    sync_vector_db()