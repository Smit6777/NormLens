# Architecture Overview

## System Context
The BIS Recommendation System Backend is a Python-based FastAPI application providing advanced extraction, vector similarity matching, and compliance validation for tender documents. It operates completely disconnected from live web scraping in production to ensure high availability, relying on a pre-curated Knowledge Base.

## Core Layers

1. **API Layer (`app/api/`)**:
   - Built on FastAPI.
   - Responsible for HTTP routing, CORS headers, rate limiting (100 req/hr), and authentication (API keys).
   
2. **Services Layer (`app/services/`)**:
   - `extractor.py`: Extracts and parses raw text from PDFs or strings. Includes security validation.
   - `llm_extractor.py`: Optional fallback extraction via Large Language Models.
   - `vector_db.py`: Wraps FAISS and `sentence-transformers` for lightning-fast high-dimensional vector search.
   - `matcher.py`: Correlates raw requirements against the vector index.
   - `compliance.py`: Assesses standards against real QCO mappings and standard status.
   - `gap_analysis.py` & `fixer.py`: Analyzes matched gaps and generates actionable fix recommendations.
   
3. **Data Layer (`app/data_layer/`)**:
   - `repository.py`: In-memory index of `bis_metadata.json`, `bis_compliance.json`, `qco_mapping.json`, and `normative_graph.json`.
   
4. **Core Utilities (`app/core/`)**:
   - `config.py`: Environment configuration via pydantic.
   - `cache.py`: LRU caching for `/search` queries.
   - `logging_config.py`: Structured JSON logging with injected UUID Request IDs.

## Data Flow (Analyze)
1. Request -> `POST /analyze` (File or Text)
2. Extractor splits document into `ExtractedRequirement` models.
3. Matcher converts requirements to embeddings and queries `FAISS`.
4. Compliance engine cross-references matches against QCOs.
5. Gap Analyzer looks for missing mandatory certifications.
6. Fixer yields actionable suggestions.
7. Aggregated JSON payload is returned to the user, and an asynchronous Webhook is fired if a `callback_url` was specified.
