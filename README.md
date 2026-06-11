# DocuMind

AI-powered PDF Question Answering System built using React, FastAPI, FAISS, Sentence Transformers, and Groq.

## Features

* Upload PDF documents
* Ask natural language questions
* Semantic search using vector embeddings
* AI-generated answers using Groq
* Modern chat interface
* Chat history support

## Tech Stack

### Frontend

* React
* Vite
* Axios

### Backend

* FastAPI
* LangChain
* FAISS
* Sentence Transformers
* Groq

## Screenshots

### Home Screen

![Home](screenshots/home.png)

### PDF Upload

![Upload](screenshots/upload.png)

### Chat Interface

![Chat](screenshots/chat.png)

## Run Locally

### Backend

```bash
cd backend
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```
