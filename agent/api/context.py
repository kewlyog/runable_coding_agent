from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from agent.context import context_manager

router = APIRouter()

class SaveContextRequest(BaseModel):
    job_id: str
    context: Dict[str, Any]

class PruneContextRequest(BaseModel):
    job_id: str
    max_tokens: Optional[int] = 1000000

@router.post("/save")
def save_context_api(req: SaveContextRequest):
    context_manager.save_context(req.job_id, req.context)
    return {"status": "ok"}

@router.get("/load")
def load_context_api(job_id: str):
    ctx = context_manager.load_context(job_id)
    return {"context": ctx}

@router.post("/prune")
def prune_context_api(req: PruneContextRequest):
    ctx = context_manager.load_context(req.job_id)
    pruned = context_manager.prune_context(ctx, req.max_tokens)
    return {"context": pruned} 