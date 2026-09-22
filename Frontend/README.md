# BharatStandards.AI
> **SIH 2026 Problem Statement 26108**: AI-Powered Recommendation of Applicable Indian Standards for Procurement Specifications

An enterprise-grade, institutional web platform designed for government and enterprise procurement teams across India. It seamlessly translates complex technical tender specifications into applicable Bureau of Indian Standards (BIS) codes, active Quality Control Orders (QCO), normative references, and certification compliance requirements.

---

## Key Features

1. **Modern Indian Institutional Aesthetics**:
   - Palette: Forest Green (`#16835B`, `#0B6045`), Information Blue (`#2474A8`), Saffron accents (`#F39A32`), Warm Cream (`#FFFDF8`), and Soft Background (`#F7F8F5`).
   - Clean whitespace, no cyber graphics, no dark mode, no visual clutter.
   - Elegant Indian institutional architectural vector illustration.

2. **Streamlined User Experience**:
   - **Home**: Single main card with dual modes ("Describe Requirement" and "Upload Tender Document"), sample chips, and 4 compact trust indicators.
   - **New Analysis**: Clean 3-stage stepper (`1 Input` → `2 Analysis` → `3 Results`) with tender PDF upload detection.
   - **Dedicated Processing Screen**: Smooth circular progress indicator with 7-stage vertical timeline (Reading specification → Extracting requirements → Identifying category → Searching Knowledge Base → Finding related standards → Checking versions → Preparing recommendations).
   - **Institutional Results Dashboard**:
     - Submitted requirement & status badge
     - 4 compact metric cards (Standards Found, Related Standards, Version Status, Certification)
     - Section 1: AI Understanding (Product, Application, Technical tags)
     - Section 2: Recommended Indian Standards (Top 3 cards with relevance %, status badge, details button)
     - Section 3: Why Recommended breakdown (Checklist matching parameters)
     - Section 4: Related Standards (Clean institutional relationship graph)
     - Section 5: Version & Amendments horizontal timeline (2018 → 2020 → 2023 → 2026)
     - Section 6: Certification Guidance (BIS Product Certification, CRS, Hallmarking)
     - Section 7: Information Verification box (Knowledge base audit)
     - Actions: `[ Start New Analysis ]` and `[ Export Report ]`
   - **Standards Catalog**: Searchable Bureau of Indian Standards database with filters for category, status, and year.
   - **Analysis History**: Audit log of past evaluations with immediate re-inspection.
   - **About Section**: Detailed mission context on SIH 2026 PS 26108.

---

## How to Run

### Connect to Live Backend
This frontend is dynamically integrated with the FastAPI backend. It requires the backend API to be running on `http://127.0.0.1:8000`.

**Do not just double-click `index.html`.** You must serve it over HTTP to prevent CORS and fetch errors.

1. First, ensure the Python backend is running (see the `Backend/README.md`).
2. Serve this directory using any static web server. For example, using Node.js:
```bash
npx http-server -p 3000
```
3. Navigate to `http://127.0.0.1:3000` in your browser.

All data, including recommended standards, version timelines, and certification requirements, are now pulled dynamically from the live AI engine.
