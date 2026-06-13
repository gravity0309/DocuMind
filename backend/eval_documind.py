"""
DocuMind RAG Evaluation Script
================================
Drop this file into your backend/ folder.
Run: python eval_documind.py
"""

import time
import json
import requests
from sentence_transformers import SentenceTransformer, util

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
BASE_URL = "http://localhost:8000"
TEST_PDF  = "test_doc.pdf"

# ─────────────────────────────────────────────
# TEST CASES (DEA-C01 Cheat Sheet)
# ─────────────────────────────────────────────
TEST_CASES = [
    {
        "question": "How do you make S3 customer records immutable for 7 years so even root cannot delete them?",
        "expected_answer": "Enable S3 Object Lock in compliance mode.",
        "keywords": ["S3 Object Lock", "compliance mode", "immutable"]
    },
    {
        "question": "Which AWS service detects PII in S3 datasets automatically with minimal manual work?",
        "expected_answer": "Amazon Macie using automated sensitive data discovery.",
        "keywords": ["Amazon Macie", "PII", "sensitive data discovery"]
    },
    {
        "question": "How do you redact PII dynamically when reading objects from S3?",
        "expected_answer": "Use S3 Object Lambda with a Lambda function containing redaction logic.",
        "keywords": ["S3 Object Lambda", "Lambda", "redact", "PII"]
    },
    {
        "question": "How do you encrypt S3 objects so only specific employees can access the keys?",
        "expected_answer": "Use SSE-KMS and restrict access with key policies.",
        "keywords": ["SSE-KMS", "key policies", "encrypt", "S3"]
    },
    {
        "question": "What is the solution for petabytes of S3 data with unpredictable access but millisecond retrieval required?",
        "expected_answer": "Enable S3 Intelligent-Tiering with default access tiers.",
        "keywords": ["S3 Intelligent-Tiering", "millisecond", "unpredictable"]
    },
    {
        "question": "How do you automatically archive cold S3 data after 90 days at lowest cost?",
        "expected_answer": "Use an S3 Lifecycle rule to transition to Glacier Flexible or Deep Archive.",
        "keywords": ["Lifecycle", "Glacier", "archive", "90 days"]
    },
    {
        "question": "How do you get alerts with username when users violate S3 access policies?",
        "expected_answer": "Enable CloudTrail data events and forward to CloudWatch for alarms.",
        "keywords": ["CloudTrail", "CloudWatch", "alarms", "S3 access"]
    },
    {
        "question": "How do you record all write operations to an S3 bucket into another S3 bucket?",
        "expected_answer": "Enable CloudTrail data events (write-only) with the destination bucket configured.",
        "keywords": ["CloudTrail", "data events", "write-only", "S3"]
    },
    {
        "question": "How do you restrict PII column access in S3 JSON files to a limited group?",
        "expected_answer": "Use AWS Lake Formation with column and row-level permissions.",
        "keywords": ["Lake Formation", "column-level", "row-level", "PII"]
    },
    {
        "question": "How do analysts in multiple countries access only their own country's data in S3?",
        "expected_answer": "Register S3 in Lake Formation and enforce row-level security with country column filters.",
        "keywords": ["Lake Formation", "row-level security", "country", "S3"]
    },
    {
        "question": "How do you implement a data mesh with centralized governance?",
        "expected_answer": "Use S3 for storage, Glue for catalog and ETL, Athena for queries, and Lake Formation for governance.",
        "keywords": ["S3", "Glue", "Athena", "Lake Formation", "data mesh"]
    },
    {
        "question": "How do you share curated tables across AWS accounts with governance?",
        "expected_answer": "Use Lake Formation resource sharing with LF-tags.",
        "keywords": ["Lake Formation", "cross-account", "resource sharing", "LF-tags"]
    },
    {
        "question": "How do you provide row and column level controls for S3 queries across Athena, Redshift, and EMR?",
        "expected_answer": "Use Lake Formation with LF-tag policies and fine-grained filters.",
        "keywords": ["Lake Formation", "LF-tag", "row", "column", "Athena", "Redshift", "EMR"]
    },
    {
        "question": "How do you implement role-based access control for 100+ Redshift users?",
        "expected_answer": "Use Redshift Role-Based Access Control (RBAC).",
        "keywords": ["Redshift", "RBAC", "role-based", "access control"]
    },
    {
        "question": "How do you create cross-region snapshot copies for a KMS-encrypted Redshift cluster?",
        "expected_answer": "Enable snapshot copy and use a snapshot copy grant in the destination region.",
        "keywords": ["Redshift", "snapshot copy", "KMS", "cross-region", "grant"]
    },
    {
        "question": "How do you store and rotate Redshift credentials used by Glue jobs?",
        "expected_answer": "Store credentials in AWS Secrets Manager and grant Glue access via IAM role.",
        "keywords": ["Secrets Manager", "Glue", "Redshift", "credentials", "rotation"]
    },
    {
        "question": "How do you fix slow Redshift COPY operations caused by many small files?",
        "expected_answer": "Stage files to S3 and run COPY with a MANIFEST after compaction.",
        "keywords": ["Redshift", "COPY", "MANIFEST", "compaction", "S3"]
    },
]

# ─────────────────────────────────────────────
# METRIC FUNCTIONS
# ─────────────────────────────────────────────

def context_recall(retrieved_chunks: list, keywords: list) -> float:
    if not keywords or not retrieved_chunks:
        return 0.0
    combined = " ".join(retrieved_chunks).lower()
    hits = sum(1 for kw in keywords if kw.lower() in combined)
    return hits / len(keywords)


def answer_similarity(generated: str, expected: str, model) -> float:
    emb1 = model.encode(generated, convert_to_tensor=True)
    emb2 = model.encode(expected, convert_to_tensor=True)
    return float(util.cos_sim(emb1, emb2).item())


# ─────────────────────────────────────────────
# API HELPERS
# ─────────────────────────────────────────────

def upload_pdf(pdf_path: str):
    """Upload PDF. Returns session_id string on success, None on failure."""
    print(f"\n📄 Uploading {pdf_path}...")
    try:
        with open(pdf_path, "rb") as f:
            response = requests.post(
                f"{BASE_URL}/upload",
                files={"file": (pdf_path, f, "application/pdf")},
                timeout=300
            )
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            print(f"✅ Upload successful — session_id: {session_id}")
            return session_id
        else:
            print(f"❌ Upload failed: {response.status_code} — {response.text}")
            return None
    except FileNotFoundError:
        print(f"❌ PDF not found: {pdf_path}")
        print("   → Rename your PDF to 'test_doc.pdf' and put it in backend/")
        return None
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {BASE_URL}")
        print("   → Run: uvicorn main:app --reload")
        return None


def ask_question(question: str, session_id: str) -> dict:
    """Send question with the real session_id from upload."""
    payload = {"question": question, "session_id": session_id}

    start = time.time()
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json=payload,
            timeout=120
        )
        latency_ms = (time.time() - start) * 1000

        if response.status_code == 200:
            data = response.json()
            answer  = data.get("answer", data.get("response", str(data)))
            sources = data.get("sources", data.get("context", data.get("chunks", [])))
            if sources and isinstance(sources, list) and len(sources) > 0:
                if isinstance(sources[0], dict):
                    sources = [s.get("text", s.get("content", str(s))) for s in sources]
            return {"answer": answer, "sources": sources, "latency_ms": latency_ms}
        else:
            return {"answer": "", "sources": [], "latency_ms": latency_ms,
                    "error": f"{response.status_code}: {response.text}"}
    except Exception as e:
        return {"answer": "", "sources": [], "latency_ms": 0, "error": str(e)}


# ─────────────────────────────────────────────
# MAIN EVAL LOOP
# ─────────────────────────────────────────────

def run_evaluation():
    print("=" * 60)
    print("  DocuMind RAG Evaluation")
    print("=" * 60)

    # Step 1: Upload PDF and get real session_id
    session_id = upload_pdf(TEST_PDF)
    if not session_id:
        print("\n⚠️  Skipping eval — fix upload issue first.")
        return

    # Step 2: Load embedding model
    print("\n🔄 Loading sentence-transformers model...")
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    print("✅ Model loaded")

    # Step 3: Run each test case
    results = []
    print(f"\n🧪 Running {len(TEST_CASES)} test questions...\n")

    for i, case in enumerate(TEST_CASES, 1):
        print(f"  [{i}/{len(TEST_CASES)}] {case['question'][:60]}...")

        response = ask_question(case["question"], session_id)

        if "error" in response:
            print(f"         ⚠️  Error: {response['error']}")
            results.append({
                "question": case["question"],
                "context_recall": 0.0,
                "answer_similarity": 0.0,
                "latency_ms": 0.0,
                "error": response["error"]
            })
            continue

        cr  = 0.0  # backend does not return sources
        sim = answer_similarity(response["answer"], case["expected_answer"], embed_model)
        lat = response["latency_ms"]

        results.append({
            "question":          case["question"],
            "generated_answer":  response["answer"],
            "expected_answer":   case["expected_answer"],
            "context_recall":    cr,
            "answer_similarity": sim,
            "latency_ms":        lat,
        })
        print(f"         similarity={sim:.2f}  latency={lat:.0f}ms")

    # Step 4: Aggregate
    valid = [r for r in results if "error" not in r]
    if not valid:
        print("\n❌ No valid results — check your endpoint configuration.")
        return

    avg_similarity = sum(r["answer_similarity"]  for r in valid) / len(valid)
    avg_latency    = sum(r["latency_ms"]         for r in valid) / len(valid)
    errors         = len(results) - len(valid)

    # Step 5: Print summary
    print("\n" + "=" * 60)
    print("  EVALUATION RESULTS")
    print("=" * 60)
    print(f"  Questions evaluated  : {len(valid)} / {len(TEST_CASES)}")
    print(f"  Errors               : {errors}")
    print(f"  ────────────────────────────────────")
    print(f"  Avg Answer Similarity: {avg_similarity:.2f} / 1.00")
    print(f"  Avg Response Latency : {avg_latency:.0f} ms  ({avg_latency/1000:.1f}s)")
    print(f"  Note: Context recall skipped — backend does not return")
    print(f"        retrieved chunks in /ask response. See Option B below")
    print(f"        to add this metric by exposing sources from backend.")
    print("=" * 60)

    print("\n📋 RESUME BULLET (copy this):")
    print("-" * 60)
    print(
        f"Evaluated RAG pipeline on {len(valid)}-query test set; achieved "
        f"{avg_similarity:.2f} avg semantic similarity score (sentence-transformers) "
        f"across AWS DEA-C01 domain questions; avg end-to-end latency {avg_latency/1000:.1f}s."
    )
    print("-" * 60)

    output_file = "eval_results.json"
    with open(output_file, "w") as f:
        json.dump({
            "summary": {
                "total_questions":       len(TEST_CASES),
                "evaluated":             len(valid),
                "errors":                errors,
                "avg_answer_similarity": round(avg_similarity, 4),
                "avg_latency_ms":        round(avg_latency, 2),
                "note":                  "context_recall not measured: /ask does not return source chunks"
            },
            "results": results
        }, f, indent=2)
    print(f"\n💾 Full results saved to: {output_file}\n")
    print("💡 Option B: To also get context recall, add 'sources' to your")
    print("   /ask response in main.py and re-run this script.\n")


if __name__ == "__main__":
    run_evaluation()

