# Deployment Guide

The backend is fully containerized and easily deployable to Render, Railway, AWS ECS, or any standard Docker swarm.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Set to `production` in live environments. |
| `API_KEY` | `test-api-key` | Standard access key. |
| `ADMIN_API_KEY` | `admin-api-key` | Used solely for `/rebuild-index`. |
| `RATE_LIMIT` | `100/hour` | Rate limit threshold. |
| `MAX_UPLOAD_SIZE_MB` | `10` | Caps upload file size in MB. |
| `ENABLE_CACHE` | `true` | Turns on the LRU search cache. |
| `ENABLE_HINDI` | `false` | Enables simple Hindi translation for queries. |
| `ENABLE_LLM_EXTRACTOR`| `false` | Fallback LLM-based parsing. |

## 1. Docker Compose (Simplest)
```bash
docker-compose up -d --build
```
This maps port `8000` to the host and mounts the `./data` directory externally so vector indices and analytics data persist across container restarts.

## 2. Render / Railway
1. Connect your GitHub repository.
2. Set the root directory to `backend/`.
3. Render will auto-detect the `Dockerfile` and build it.
4. Ensure you define `API_KEY` and `ADMIN_API_KEY` in the service's Environment Variables dashboard.
5. Provide a persistent disk volume mapping to `/app/data` so the vector store doesn't rebuild from scratch every deploy (though rebuilding is fast).

## 3. CI/CD (GitHub Actions)
A workflow exists at `.github/workflows/ci.yml`. It runs tests automatically on pushes to `main`. 
