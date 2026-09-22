# Team Handoff - Frontend & Deployment

Welcome to the BIS Standard Recommendation Backend! The backend is now fully completed, tested, and hardened for production deployment.

## What Frontend Needs to Know
1. **CORS is Configured**: The backend currently permits `allow_origins=["*"]`. You can query it directly from your React/Vue `localhost` development servers without issues. (Change this to your specific UI domain prior to a live launch by editing `main.py`).
2. **API Keys**: Every request (except `/health` and `/metrics`) requires an `X-API-Key` header. Use the value configured in `API_KEY` (default: `test-api-key`).
3. **Primary Endpoint**: You will spend 99% of your time interacting with `POST /api/v1/analyze`. Pass your PDF in the `file` form-data parameter.
4. **Export Buttons**: You can easily wire an "Export as CSV" button on the UI by hitting `POST /api/v1/analyze/export` with the same arguments. It will return a downloadable file buffer.
5. **Postman Collection**: A fully populated `postman_collection.json` is provided in the root directory. Import this into Postman to instantly test and visualize the JSON contracts.

## Production Checklist (Ops/DevOps)
- [ ] Mount the `/app/data` volume persistently in your deployment container so analytics and vector indices aren't wiped on restart.
- [ ] Ensure `ENABLE_LLM_EXTRACTOR` and `ENABLE_HINDI` are set correctly based on your hardware budget (they consume marginally more resources).
- [ ] Change `API_KEY` and `ADMIN_API_KEY` to secure strings.

## End of Backend Workstream
All 11 phases are complete. The vector store is fast, the gap analysis works, QCO validations are active, rate limiting and tracing are enabled, and the tests pass. 
Happy building!
