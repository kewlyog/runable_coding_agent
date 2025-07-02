# xdot Tool API
# Exposes endpoints to control GUI applications via xdotool. 

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import subprocess

router = APIRouter()

class XdotActionRequest(BaseModel):
    xdotool_args: List[str]

@router.post("/exec")
def exec_xdot(req: XdotActionRequest):
    if not req.xdotool_args:
        raise HTTPException(status_code=400, detail="No xdotool arguments provided")
    try:
        result = subprocess.run(
            ["xdotool"] + req.xdotool_args,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"xdotool error: {e}") 