# Phase 10: Advanced Features

This document outlines the advanced features added to the BIS Recommendation Engine backend during Phase 10.

## 1. Optional LLM Extraction (`app/services/llm_extractor.py`)
Provides a fallback mechanism for heavily unstructured PDFs where rule-based heuristics fail. 
- **Configuration:** Set `ENABLE_LLM_EXTRACTOR=true` in your `.env`.
- **Behavior:** Operates upstream in `/analyze`. If enabled, it attempts extraction first. If it yields results, the rule-based extractor is bypassed, saving time. Otherwise, it gracefully falls back to rule-based extraction.

## 2. Multilingual Support (`app/services/multilingual.py`)
Enables parsing Hindi terminology in search and extraction.
- **Configuration:** Set `ENABLE_HINDI=true`.
- **Behavior:** Intercepts incoming queries (e.g., in `/search` and `/recommend`) and applies a translation dictionary to map common terms like "सीमेंट" to "cement", allowing the underlying vector matcher (which operates in English) to match effectively.

## 3. Bulk Tender Analysis (`POST /api/v1/analyze-bulk`)
Allows client applications to submit batches of PDFs in a single HTTP request.
- **Location:** `app/api/endpoints_bulk.py`
- **Behavior:** Validates that the request contains at most 10 PDFs. Processes each sequentially, yielding an aggregate JSON containing results mapped by filename.

## 4. Export Reports (`POST /api/v1/analyze/export`)
Allows users to instantly download the analysis payload as a formatted CSV file.
- **Behavior:** Executes the standard `/analyze` logic but intercepts the JSON response and serializes it using the `csv` module in `app/services/export.py`. It yields a `text/csv` attachment response containing requirement texts, matched standard IS numbers, scores, and detected compliance gaps.

## 5. Webhook Notifications
Supports asynchronous workflows for heavy extraction jobs.
- **Behavior:** Passing the `callback_url` form-data parameter to `POST /api/v1/analyze` will queue a background task (`fastapi.BackgroundTasks`). Once the analysis completes, the server executes a non-blocking POST request to the webhook URL containing the JSON dump of the `AnalyzeResponse`.

## 6. Caching Layer (`app/core/cache.py`)
A fast, in-memory LRU caching layer configured via `ENABLE_CACHE=true`.
- **Behavior:** MD5-hashes request arguments (like `query` and `top_k` in `/search`). Repeated searches instantly return the cached result payload, avoiding expensive vector distance computations. The cache is automatically cleared when `POST /rebuild-index` is invoked to prevent stale hits.

## 7. Historical Trend Analysis (`app/services/analytics.py`)
Tracks the frequency of standard recommendations.
- **Behavior:** Whenever the matcher successfully maps a requirement to an IS standard (via `/analyze` or `/recommend`), the occurrence is logged in `data/analytics.json`.
- **Endpoint:** `GET /api/v1/standards/{is_number}/usage` returns the total recommendation count and a plain-English trend message.
