# Code Execution Tool API
# Exposes endpoints to execute Python, TypeScript, etc. with context management. 

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import subprocess
import tempfile
import os
from agent.context import context_manager

router = APIRouter()

class CodeExecRequest(BaseModel):
    code: str
    language: str  # 'python' or 'typescript'
    timeout: int = 10  # seconds
    job_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@router.post("/exec")
def exec_code(req: CodeExecRequest):
    # Load context if job_id is provided
    ctx = None
    if req.job_id:
        ctx = context_manager.load_context(req.job_id)
    # (Context can be used here for advanced features)

    if req.language not in ("python", "typescript"):
        raise HTTPException(status_code=400, detail="Unsupported language")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.py' if req.language == 'python' else '.ts') as tmp:
        tmp.write(req.code.encode())
        tmp.flush()
        tmp_path = tmp.name

    if req.language == "python":
        cmd = ["python3", tmp_path]
    else:
        cmd = ["node", "--loader", "ts-node/esm", tmp_path]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=req.timeout,
            check=False,
        )
        os.unlink(tmp_path)
        # Save context if provided
        if req.job_id and req.context is not None:
            context_manager.save_context(req.job_id, req.context)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "context": ctx if ctx is not None else {},
        }
    except subprocess.TimeoutExpired:
        os.unlink(tmp_path)
        return {
            "stdout": "",
            "stderr": f"Code execution timed out after {req.timeout} seconds",
            "exit_code": -1,
            "context": ctx if ctx is not None else {},
        }
    except Exception as e:
        os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Code execution error: {e}") 