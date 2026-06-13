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
Evaluation
DocuMind was evaluated on a manually curated 31-query test set derived from AWS DEA-C01 domain-specific content.
Results
MetricScoreAnswer Semantic Similarity0.51 / 1.00Avg End-to-End Latency35.9sTest Queries31
Methodology

Answer Semantic Similarity — cosine similarity between LLM-generated answers and ground truth answers, computed using sentence-transformers/all-MiniLM-L6-v2 embeddings
Latency — measured end-to-end from question submission to answer received, including FAISS vector retrieval and Groq LLaMA3-8b generation


Note: Latency reflects free-tier Groq API and Railway deployment constraints. Production deployment with dedicated compute would yield significantly lower latency.

How to Reproduce
bash# 1. Start the backend
cd backend
uvicorn main:app --reload

# 2. In a separate terminal, run evaluation
cd backend
python eval_documind.py
Full results are saved to eval_results.json.