# Agent API Entrypoint
# Starts the REST API server exposing all agent tools. 

import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from fastapi import FastAPI, Depends, HTTPException, Header

from agent.api import shell, code, xdot, fs, context

def get_api_key(x_api_key: str = Header(...)):
    expected = os.environ.get("AGENT_API_KEY")
    if not expected or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API Key")

app = FastAPI(title="Runable Coding Agent API", dependencies=[Depends(get_api_key)])

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}

# Register tool routers (placeholders for now)
app.include_router(shell.router, prefix="/shell", tags=["shell"])
app.include_router(code.router, prefix="/code", tags=["code"])
app.include_router(xdot.router, prefix="/xdot", tags=["xdot"])
app.include_router(fs.router, prefix="/fs", tags=["filesystem"])
app.include_router(context.router, prefix="/context", tags=["context"]) 