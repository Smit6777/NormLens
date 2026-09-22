# Track 03 Integration Guide (AI & Compliance Backend)

## 1. What Track 03 Adds
Track 03 implements the core intelligence engine for the BIS Recommendation System. It replaces static mock data with a dynamic AI pipeline that processes tender documents through:
- **Requirement Extraction**: Parses raw strings and PDFs into structured semantic units.
- **Vector Search / FAISS**: Uses the `all-mpnet-base-v2` embedding model to query an optimized FAISS vector store of BIS standards.
- **Compliance & Gap Analysis**: Evaluates matching standards against QCO mappings, determining required certifications and highlighting compliance gaps.
- **AI Fixer**: Generates actionable edits for non-compliant requirement text.

## 2. Final Endpoint Mapping

The unified backend serves both the Frontend Application and the Track 03 APIs via `FastAPI`.

| Capability | HTTP Route | Description |
|---|---|---|
| **Frontend UI** | `GET /frontend/index.html` | The static HTML frontend imported from Track 01. |
| **System Health** | `GET /api/v1/health` | Service and vector index status. |
| **Document Analysis** | `POST /api/v1/analyze` | **Primary Integration Endpoint.** Parses a PDF/text and runs the full vector search, compliance, and gap analysis pipeline. |
| **Direct Search** | `POST /api/v1/search` | Raw FAISS semantic similarity search. |
| **Rebuild Index** | `POST /api/v1/rebuild-index`| Re-generates embeddings for all standard metadata in `data/`. |

## 3. API Examples (Frontend Integration)

### **Request: POST `/api/v1/analyze`**
You can invoke this directly from `app.js` using `fetch`.
```javascript
const formData = new FormData();
// Add either a raw string or a File object
formData.append("text", "Require 90W Outdoor LED Street Lighting with IP66 housing");
// formData.append("file", fileInput.files[0]); 

const response = await fetch("http://localhost:8000/api/v1/analyze", {
    method: "POST",
    headers: {
        "X-API-Key": "test-api-key"
    },
    body: formData
});
const data = await response.json();
```

### **Response Schema Example**
```json
{
  "requirements": [
    {
      "requirement_id": "REQ-001",
      "raw_text": "Require 90W Outdoor LED Street Lighting with IP66 housing"
    }
  ],
  "recommendations": {
    "REQ-001": [
      {
        "is_number": "IS 10322 (Part 5/Sec 3): 2012",
        "title": "Luminaires: Particular Requirements - Luminaires for Road and Street Lighting",
        "system_match_score": 0.85,
        "match_reasons": ["Semantic similarity to Street Lighting and IP66"],
        "compliance": {
          "status": "mandatory",
          "certification_type": "ISI Mark"
        },
        "evidence": ["Matched QCO mappings for Luminaires"],
        "source_ids": ["qco_electrical_2024"],
        "confidence": "HIGH",
        "verification_required": []
      }
    ]
  },
  "fix_suggestions": [],
  "gaps": []
}
```

## 4. Required Environment Variables
The backend relies on `.env` configuration (see `.env.example`).
- `API_KEY`: Key required by frontend to talk to the backend (`test-api-key`).
- `ADMIN_API_KEY`: Used strictly for `POST /api/v1/rebuild-index`.
- `ENABLE_LLM_EXTRACTOR`: Fallback deep NLP extraction (Default: `false`).
- `ENABLE_HINDI`: Multilingual string parsing (Default: `false`).

## 5. Rebuilding the Vector Index
The FAISS index is built and cached inside `data/`. If you add new JSON records to `bis_metadata.json`, hit the `POST /api/v1/rebuild-index` endpoint using the `ADMIN_API_KEY` to sync the vector database.

## 6. Known Limitations
- **Local BIS Knowledge Base Only**: To guarantee uptime and avoid IP bans, the system queries local curated JSON datasets instead of live web scraping.
- **NOT VERIFIED States**: If an IS number is processed but lacks QCO/Compliance data in our curated sets, it returns `NOT VERIFIED` rather than hallucinating status.
- **AI Recommendation Only**: `system_match_score` is a semantic similarity score, not proof of strict legal compliance. Human verification is strictly required for official municipal tenders.
