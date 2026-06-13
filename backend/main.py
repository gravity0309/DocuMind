from collections import deque
from pathlib import Path
from uuid import uuid4

import shutil
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag import build_qa_chain

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}


@app.get("/")
def home():
    return {"message": "DocuMind API Running"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    session_id = str(uuid4())
    safe_filename = Path(file.filename).name
    path = f"uploaded_{session_id}_{safe_filename}"

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    sessions[session_id] = {
        "qa_chain": build_qa_chain(path),
        "history": deque(maxlen=10),
        "filename": safe_filename,
    }

    return {
        "message": "PDF processed successfully",
        "session_id": session_id,
        "filename": safe_filename,
    }


class Question(BaseModel):
    session_id: str
    question: str


def format_conversation_history(history):
    if not history:
        return "No previous conversation."

    turns = []
    for index, item in enumerate(history, start=1):
        turns.append(
            f"Turn {index}\n"
            f"User: {item['question']}\n"
            f"Assistant: {item['answer']}"
        )

    return "\n\n".join(turns)


@app.post("/ask")
async def ask_question(body: Question):
    session = sessions.get(body.session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="This chat session was not found. Please upload the PDF again.",
        )

    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    qa_chain = session["qa_chain"]
    history = session["history"]
    conversation_history = format_conversation_history(history)
    retrieval_query = f"{conversation_history}\n\nCurrent question: {question}"

    docs = qa_chain["retriever"].invoke(retrieval_query)
    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are DocuMind, an AI assistant that answers questions about an uploaded PDF.
Use the PDF context and the previous conversation to answer the current question.
If the user refers to earlier answers with phrases like "those skills" or "that point",
resolve the reference from the conversation history.
If the answer is not supported by the PDF context, say you could not find it in the uploaded PDF.

Previous conversation:
{conversation_history}

PDF context:
{context}

Current question:
{question}
"""

    response = qa_chain["llm"].invoke(prompt)
    answer = response.content

    history.append(
        {
            "question": question,
            "answer": answer,
        }
    )

return {
        "answer": answer,
        "session_id": body.session_id,
        "sources": [doc.page_content for doc in docs],
    }   