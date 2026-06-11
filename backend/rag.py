from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()


def build_qa_chain(pdf_path: str):
    # Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    print(f"Documents loaded: {len(documents)}")

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(documents)

    print(f"Chunks created: {len(chunks)}")

    # Safety check
    if len(chunks) == 0:
        raise Exception(
            "No text extracted from PDF. PDF may be scanned, empty, or protected."
        )

    # Embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Creating FAISS vector store...")

    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )

    print("FAISS vector store created successfully.")

    # Groq LLM
    llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

    return {
        "llm": llm,
        "retriever": vectorstore.as_retriever()
    }