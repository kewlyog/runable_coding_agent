# Filesystem Tool API
# Exposes endpoints to create, edit, move, and manage files securely. 

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter()

WORKSPACE = "/home/agent/workspace"
os.makedirs(WORKSPACE, exist_ok=True)

def safe_path(path: str) -> str:
    full = os.path.abspath(os.path.join(WORKSPACE, path))
    if not full.startswith(WORKSPACE):
        raise HTTPException(status_code=400, detail="Invalid path")
    return full

class WriteRequest(BaseModel):
    path: str
    content: str

class MoveRequest(BaseModel):
    src: str
    dst: str

class DeleteRequest(BaseModel):
    path: str

@router.post("/write")
def write_file(req: WriteRequest):
    p = safe_path(req.path)
    with open(p, "w") as f:
        f.write(req.content)
    return {"status": "ok"}

@router.get("/read")
def read_file(path: str):
    p = safe_path(path)
    if not os.path.exists(p):
        raise HTTPException(status_code=404, detail="File not found")
    with open(p) as f:
        return {"content": f.read()}

@router.post("/move")
def move_file(req: MoveRequest):
    src = safe_path(req.src)
    dst = safe_path(req.dst)
    os.rename(src, dst)
    return {"status": "ok"}

@router.post("/delete")
def delete_file(req: DeleteRequest):
    p = safe_path(req.path)
    if os.path.isdir(p):
        os.rmdir(p)
    else:
        os.remove(p)
    return {"status": "ok"} 