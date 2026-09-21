"""Bulk analysis endpoints."""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from typing import List
from app.main import AppState
from app.api.deps import get_services
from app.api.endpoints import analyze

router = APIRouter()

@router.post("/analyze-bulk")
async def analyze_bulk(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    services: AppState = Depends(get_services)
):
    """Analyze multiple PDFs sequentially."""
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per request.")
        
    results = []
    for f in files:
        # Re-use the individual analyze logic
        resp = await analyze(background_tasks, file=f, text=None, callback_url=None, services=services)
        results.append({
            "filename": f.filename,
            "analysis": resp.model_dump(mode="json")
        })
        
    return {"results": results}
