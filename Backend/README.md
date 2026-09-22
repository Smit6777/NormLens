# BIS Standard Recommendation & Compliance Auditor — Backend

AI-assisted tool that maps government tender/procurement requirements to
applicable Bureau of Indian Standards (BIS), with **evidence, provenance,
and confidence on every claim**.

> **Decision-support only.** Every output must be verified against the
> current BIS portal before official use.

## Non-negotiable rules

| # | Rule |
|---|------|
| 1 | **Zero hallucination** — never invent an IS number, title, QCO mapping, evidence, or official score. |
| 2 | **NOT FOUND ≠ DOES NOT EXIST** — return `NOT_VERIFIED`, not 404. |
| 3 | **Traceability** — every claim carries `source_ids` and `evidence`. |
| 4 | **Immutable requirements** — the fixer proposes, never silently alters. |
| 5 | **AI ≠ Fact** — `system_match_score` (AI ranking) is separate from `confidence` (compliance verification). |

## Architecture

```
Tender PDF/Text
  → Extraction (pdfplumber / text parser)
  → Requirement Extraction (rule-based NLP)
  → Semantic Embedding (sentence-transformers)
  → FAISS Vector Search
  → Reranking (weighted multi-signal)
  → Compliance Engine (status, version, QCO, normative graph)
  → Evidence & Provenance Resolution
  → Gap Analysis (superseded, missing QCO, unverified citations)
  → AI Fixer (proposed revisions with evidence)
  → Structured API Response
  → Frontend Display
```

### Project structure

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py            # FastAPI dependency injection
│   │   └── endpoints.py       # All API routes
│   ├── core/
│   │   ├── config.py          # Environment-based settings
│   │   ├── exceptions.py      # Centralized error hierarchy
│   │   └── logging.py         # JSON-line structured logging
│   ├── data_layer/
│   │   └── repository.py      # Knowledge-base JSON loader
│   ├── models/
│   │   └── schemas.py         # Pydantic V2 request/response models
│   ├── services/
│   │   ├── compliance.py      # ComplianceEngine (Phase 4)
│   │   ├── embeddings.py      # Sentence-transformer wrapper
│   │   ├── extractor.py       # PDF/text extraction + requirement parsing
│   │   ├── fixer.py           # AIFixer (Phase 5)
│   │   ├── gap_analysis.py    # GapAnalyzer (Phase 5)
│   │   ├── index_builder.py   # Knowledge-base → FAISS index
│   │   ├── matcher.py         # Retrieval → reranking → Recommendations
│   │   ├── normative.py       # Normative reference graph traversal
│   │   ├── provenance.py      # Evidence/source resolution
│   │   ├── qco.py             # QCO lookup service
│   │   ├── reranker.py        # Multi-signal explainable reranker
│   │   └── vector_db.py       # FAISS vector store
│   └── main.py                # FastAPI app factory + lifespan
├── data/                      # Knowledge-base JSON files
├── tests/                     # 105 automated tests
├── .env.example               # Configuration template
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Setup

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
cd backend
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

### Populating the knowledge base

The five JSON files under `data/` define what the system knows. **Never
invent data** — populate only from verified BIS sources:

| File | Purpose |
|------|---------|
| `bis_metadata.json` | IS number, title, product, scope, keywords |
| `bis_compliance.json` | Standard status, versions, supersession |
| `qco_mapping.json` | Quality Control Order applicability |
| `normative_graph.json` | Inter-standard normative references |
| `sources.json` | Provenance URLs and retrieval dates |

See `data/SCHEMA.md` for the exact structure.

## Running

### Development server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The embedding model is loaded **once** during application startup (lifespan),
not per request. First startup downloads the model (~400 MB) and builds the
FAISS index from the knowledge base.

#### Running the tests

```bash
pytest -v
```

All 121 tests cover: config, logging, exceptions, repository, PDF/text
extraction, requirement parsing, embeddings, vector store, matcher,
reranker, and full API integration. Includes strict adversarial tests for domain isolation.

## API Reference

All endpoints are prefixed with `/api/v1` (configurable via `API_V1_PREFIX`).

### Health & Info

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | App info + decision-support notice |
| `GET` | `/health` | Health check with app name and environment |

### Core Pipeline

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/extract` | Extract requirements from PDF/text upload |
| `POST` | `/search` | Free-text semantic search against BIS standards |
| `POST` | `/recommend` | Match a structured requirement to standards |
| `POST` | `/audit` | Gap analysis on requirements + recommendations |
| `POST` | `/fix` | Domain-aware AI proposed fixes for identified gaps |
| `POST` | `/analyze` | **Full pipeline** — upload -> extraction -> matching -> compliance -> deduplicated gaps -> fixes |

### Reference Data

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/standards/{is_number}` | Lookup a standard — returns 200 with `NOT_VERIFIED` if unknown, never 404 |
| `POST` | `/rebuild-index` | Rebuild the vector index from the knowledge base |

### Example: Full analysis

```bash
# With a file
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "file=@tender.pdf"

# With raw text
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "text=Supply of cement complying with IS 269:1989"
```

### Response structure (`/analyze`)

```json
{
  "requirements": [
    {
      "requirement_id": "REQ-001",
      "raw_text": "...",
      "product": "Cement",
      "parameters": {"cited_standards": ["IS 269:1989"]},
      "mandatory": true
    }
  ],
  "recommendations": {
    "REQ-001": [
      {
        "is_number": "IS 269:2015",
        "title": "Ordinary Portland Cement — Specification",
        "system_match_score": 0.57,
        "match_reasons": ["Semantic similarity 0.64 ..."],
        "score_components": {"semantic_similarity": 0.64, "product_match": 1.0},
        "compliance": {
          "standard_status": "ACTIVE",
          "qco_applicable": true,
          "normative_references": ["IS 4031"],
          "qco_details": [{"product": "Cement", "in_force": true}]
        },
        "evidence": [{"source_id": "...", "verification_status": "HIGH"}],
        "confidence": "HIGH",
        "verification_required": []
      }
    ]
  },
  "gaps": [
    {
      "gap_type": "CITED_STANDARD_SUPERSEDED",
      "severity": "HIGH",
      "message": "Cited standard IS 269:1989 is superseded by IS 269:2015"
    }
  ],
  "fix_suggestions": [
    {
      "original_requirement": "...",
      "issue": "Cited standard IS 269:1989 is superseded",
      "suggested_revision": "Update reference to IS 269:2015.",
      "suggestion_status": "PROPOSED"
    }
  ]
}
```

### Error handling

| Code | Meaning |
|------|---------|
| `200` | Success (including unknown standards — returns `NOT_VERIFIED`) |
| `415` | Unsupported file type |
| `422` | Validation error (empty query, missing input, extra fields) |
| `500` | Internal server error |

## Configuration

All settings are environment-based. See [`.env.example`](.env.example) for
the full list. Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_MODEL_NAME` | `all-mpnet-base-v2` | Sentence-transformer model |
| `TOP_K_CANDIDATES` | `10` | Max candidates per requirement |
| `MIN_MATCH_SCORE` | `0.45` | Strict minimum semantic similarity threshold for relevance gate |
| `MAX_UPLOAD_SIZE_MB` | `20` | Maximum file upload size |

## Phase Completion Status

- [x] **Phase 1** — Foundation (config, logging, exceptions, schemas, repository)
- [x] **Phase 2** — Semantic search (embeddings, vector store, index builder, matcher)
- [x] **Phase 3** — Extraction + reranking (PDF/text, requirement parsing, multi-signal reranker, exact citation priority)
- [x] **Phase 4** — Compliance engine (provenance, QCO, normative graph, evidence)
- [x] **Phase 5** — Gap analysis + domain-aware AI fixer + deduplicator
- [x] **Phase 6** — FastAPI application (lifespan, endpoints, DI, error handling)
- [x] **Phase 7** — Testing + documentation (121 tests passing, README, .env.example)

## Known Limitations

- Requirement extraction is heuristic: administrative clauses are filtered
  by keyword, tables rely on pdfplumber's text ordering.
- pdfplumber is synchronous; the API runs it in a threadpool.
- Reranker weights and `MIN_MATCH_SCORE` are untuned defaults.
- No OCR support in the MVP — scanned PDFs are rejected with a clear message.
- The knowledge base ships with sample data for demonstration only.
