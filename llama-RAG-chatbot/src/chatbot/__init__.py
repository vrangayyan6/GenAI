from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompt_values import PromptValue
from langchain_core.documents import Document
from langchain_ollama.llms import OllamaLLM
from langchain_chroma import Chroma
# from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os

# Define paths relative to the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CHROMA_PATH = os.path.join(PROJECT_ROOT, "chroma_db")


def _print_prompt(prompt: PromptValue) -> PromptValue:
    """A passthrough function to print the prompt."""
    print("\n" + "=" * 50)
    print("PROMPT SENT TO LLM")
    print("=" * 50)
    print(prompt.to_string())
    print("=" * 50 + "\n")
    return prompt


def _print_retrieved_docs(docs: list[Document]) -> list[Document]:
    """A passthrough function to print the retrieved documents."""
    print("\n" + "=" * 50)
    print("RETRIEVED DOCUMENTS")
    print("=" * 50)
    if not docs:
        print("--- NO DOCUMENTS RETRIEVED ---")
    for i, doc in enumerate(docs):
        print(f"--- Document {i+1} ---\n")
        print(doc.page_content)
        if doc.metadata:
            print(f"\nMetadata: {doc.metadata}")
        print("\n" + "-" * 20)
    print("=" * 50 + "\n")
    return docs


class Chatbot:
    def __init__(self):
        self.chain = None

    def load_model(self):
        # Initialize the Ollama LLM
        model = OllamaLLM(
            model="llama3.2:1b",
            temperature=0.00001,  # Set to a very low value for deterministic responses. range from 0 to 2.
            max_tokens=512,  # Increased for potentially longer RAG answers 
            top_p=0.01,  # Set to a very low value for deterministic responses
            top_k=1,  # Set to 1 for deterministic responses
        )

        # Load the vector store and create a retriever
        if not os.path.exists(CHROMA_PATH):
            raise RuntimeError(
                f"ChromaDB not found at {CHROMA_PATH}. "
                "Please run the ingestion script first (e.g., `python -m src.util.ingest`)."
            )
        embeddings = OllamaEmbeddings(model="llama3.2:3b")  # llama3.2:3b or llama3.2:1b
        vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
        retriever = vectorstore.as_retriever()

        # RAG prompt template
        # orginal -- You are an assistant for question-answering tasks.
        #     Use the following pieces of retrieved context to answer the question.
        #     If you don't know the answer, just say that you don't know.
        #     Use three sentences maximum and keep the answer concise.
        template = """You are a highly specialized assistant for question-answering tasks. Your single most important rule is to answer questions *only* using the information found in the provided "Context" section.

            Follow these instructions strictly:
            1. Base your entire answer on the "Context" provided below. Do not use any external knowledge or prior training.
            2. If the "Context" does not contain the information needed to answer the question, you MUST respond with the exact phrase: "No information is available in the documentation to answer this question."
            3. Do not add any information that is not explicitly stated in the "Context".
            4. Be detailed and thorough in your answer, but only use details from the "Context".

            Context: {context}

            Question: {question}

            Answer:"""
        prompt = ChatPromptTemplate.from_template(template)

        # Create the RAG chain using LangChain Expression Language (LCEL)
        self.chain = (
            {
                "context": retriever | RunnableLambda(_print_retrieved_docs),
                "question": RunnablePassthrough(),
            }
            | prompt
            # | RunnableLambda(_print_prompt)
            | model
            | StrOutputParser()
        )

    def generate_response(self, user_input):
        if not self.chain:
            raise RuntimeError("Model not loaded. Please call load_model() first.")

        # The RAG chain now expects a string input for the question
        response = self.chain.invoke(user_input)
        return response.strip()

    def stream_response(self, user_input):
        """Streams the response from the RAG chain."""
        if not self.chain:
            raise RuntimeError("Model not loaded. Please call load_model() first.")
        return self.chain.stream(user_input)

    def chat(self):
        print("Chatbot is ready! Type 'exit' to quit.")
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Chatbot: Goodbye!")
                break
            response = self.generate_response(user_input)
            print(f"Chatbot: {response}")
