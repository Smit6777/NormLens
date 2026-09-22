# BharatStandards.AI
> **SIH 2026 Problem Statement 26108**: AI-Powered Recommendation of Applicable Indian Standards for Procurement Specifications

An enterprise-grade, institutional web platform designed for government and enterprise procurement teams across India. It seamlessly translates complex technical tender specifications into applicable Bureau of Indian Standards (BIS) codes, active Quality Control Orders (QCO), normative references, and certification compliance requirements.

## 🚀 Features

### 1. Robust AI-Assisted Backend Engine
- **Strict Relevance Gate**: Employs a calibrated `0.45` semantic threshold to filter out weak candidates. A tender for "Medical equipment" will confidently reject generic matches like "Electrical lighting," avoiding hallucinated compliance.
- **Exact Citation Priority**: Mathematically prioritizes exact BIS citations (e.g., `IS 8112:2013`) to Rank #1 without artificially inflating vector match scores.
- **Domain-Aware AI Fixer**: Automatically adapts its tender fix suggestions based on the identified product domain (e.g., prompting for *rated voltage* for electrical equipment vs. *technical grade* for steel/cement).
- **Gap Deduplication**: Intelligently hashes and collapses repetitive missing-reference errors, preventing UI noise.
- **Strict Isolation Contract**: "NOT FOUND = DOES NOT EXIST". If evidence is insufficient, the system gracefully outputs `NOT_VERIFIED` rather than guessing a standard.

### 2. Live Enterprise Frontend
- **Dynamic API Rendering**: Fully integrated React/Vite UI that renders data directly from the Python backend API in real-time. No hardcoded mock data.
- **Provenance & Traceability**: Visually maps QCO mandates, normative references, and standard versions directly to their offline knowledge-base source IDs.
- **Modern Institutional Aesthetics**: Designed with a clean, official color palette (Forest Green, Information Blue, Saffron, Warm Cream) appropriate for government procurement workflows.

## 📁 Project Structure

* `/Backend` - The complete FastAPI application, FAISS vector index, sentence-transformers, and offline JSON knowledge base.
* `/Frontend` - The modern web interface for submitting tenders, analyzing results, and reviewing gap analysis reports.

## 🛠️ Quick Start

### Backend Setup
```bash
cd Backend
python -m venv .venv
# Activate virtual environment (.venv\Scripts\activate on Windows)
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
*(Note: The first run will automatically download the `all-mpnet-base-v2` model from HuggingFace).*

### Frontend Setup
```bash
cd Frontend
# Run any static server, e.g., Node's http-server
npx http-server -p 3000
```
Navigate to `http://127.0.0.1:3000` to access the BharatStandards.AI dashboard!

## 🧪 Testing

The backend is fully verified with a rigorous adversarial test suite containing **121 automated tests** covering semantic matching, gap deduplication, domain isolation, and exact citation overrides.

```bash
cd Backend
pytest tests/
```

---
*Developed for the Smart India Hackathon (SIH) 2026.*
