# API Reference

**Base URL:** `/api/v1`

## 1. `GET /health`
Returns system health, including the status of the repository and vector store. 
*Requires no authentication.*

## 2. `GET /metrics`
Returns system metrics in Prometheus plaintext format.
*Requires no authentication.*

## 3. `POST /analyze`
Primary endpoint for the frontend. Accepts a PDF file or raw text.
**Headers:**
- `X-API-Key`: Your standard API key

**Form Data:**
- `file`: (Optional) PDF upload
- `text`: (Optional) Raw string of requirements
- `callback_url`: (Optional) URL to receive async POST when complete.

## 4. `POST /analyze-bulk`
Bulk analysis of multiple PDFs (max 10).
**Headers:**
- `X-API-Key`: Your standard API key

**Form Data:**
- `files`: Array of PDFs.

## 5. `POST /search`
Direct vector similarity search against the KB.
**Body:**
```json
{
  "query": "cement",
  "top_k": 5
}
```

## 6. `POST /analyze/export`
Same arguments as `/analyze`, but returns a downloadable `text/csv` spreadsheet.

## 7. `GET /standards/{is_number}/usage`
Returns historical recommendation frequency for a specific IS standard.

## 8. `POST /rebuild-index`
Forces a synchronous rebuild of the FAISS vector index and clears the LRU cache.
**Headers:**
- `X-API-Key`: Your **Admin** API key
