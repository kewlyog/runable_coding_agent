# Shell Tool API
# Exposes endpoints to execute shell commands securely in a sandboxed environment. 

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import subprocess
import shlex

router = APIRouter()

class ShellExecRequest(BaseModel):
    command: str
    cwd: Optional[str] = None
    timeout: int = 10  # seconds

@router.post("/exec")
def exec_shell(req: ShellExecRequest):
    # Sanitize and split command
    try:
        cmd = shlex.split(req.command)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid command: {e}")

    try:
        result = subprocess.run(
            cmd,
            cwd=req.cwd,
            capture_output=True,
            text=True,
            timeout=req.timeout,
            check=False,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Command timed out after {} seconds".format(req.timeout),
            "exit_code": -1,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shell execution error: {e}") 