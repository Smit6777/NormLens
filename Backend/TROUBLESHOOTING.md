# Troubleshooting Guide

## 1. Vector Index / Startup Hangs
**Issue**: Application takes 10+ seconds to boot, or requests return `ModelNotReadyError`.
**Cause**: The FAISS index is missing or out of sync with the JSON payload.
**Fix**:
The system will automatically rebuild the index upon detecting missing files. Wait a few seconds for the `index built` log. Alternatively, trigger a manual rebuild via `POST /api/v1/rebuild-index` using the `ADMIN_API_KEY`.

## 2. 403 Forbidden on Rebuild Index
**Issue**: `POST /rebuild-index` fails with 403.
**Fix**: Ensure you are passing the header `X-API-Key` configured exactly as your `ADMIN_API_KEY` (not your standard `API_KEY`).

## 3. 429 Too Many Requests
**Issue**: Immediate blocks from endpoints except `/health`.
**Fix**: You have exceeded the `RATE_LIMIT` (default 100/hour). Wait, or adjust the `.env` variable `RATE_LIMIT` to `1000/hour` and restart the application.

## 4. Emoji / Unicode Encode Errors (Windows Local Dev)
**Issue**: Running scripts yields `UnicodeEncodeError: 'charmap' codec can't encode character...`
**Fix**: Prefix python commands with standard UTF-8 encodings or run inside a modern terminal (Windows Terminal, Git Bash) rather than legacy CMD. Emojis have been removed from most core scripts to prevent this natively.

## 5. Blank Recommendations for Valid Queries
**Issue**: A valid query (e.g. "cement") returns 0 results.
**Fix**: Ensure `bis_metadata.json` has data. If it does, your FAISS index might be stale. Hit `POST /rebuild-index`.
