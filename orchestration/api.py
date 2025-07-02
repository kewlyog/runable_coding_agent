# Orchestration API
# FastAPI endpoints for /schedule and /status/:id

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from uuid import uuid4
from typing import Dict
import requests
from orchestration.vm_launcher import launch_agent_vm
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Agent Orchestration Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend's URL for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store (for demo)
jobs: Dict[str, Dict] = {}

class ScheduleRequest(BaseModel):
    task: str

@app.post("/schedule")
def schedule_job(req: ScheduleRequest):
    job_id = str(uuid4())
    vm_handle = launch_agent_vm(req.task)
    # Simulate agent API URL (in real use, this would be dynamic)
    agent_api_url = "http://localhost:5001"
    jobs[job_id] = {"task": req.task, "status": "running", "result": None, "vm_handle": vm_handle, "agent_api_url": agent_api_url}
    return {"job_id": job_id}

@app.get("/status/{job_id}")
def get_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    # For demo, mark as complete after first check
    if job["status"] == "running":
        job["status"] = "complete"
        job["result"] = "/download/{}".format(job_id)
    return {"status": job["status"], "download": job["result"], "vm_handle": job["vm_handle"]}

@app.api_route("/proxy/{job_id}/{tool}/{action}", methods=["GET", "POST"])
async def proxy_to_agent(job_id: str, tool: str, action: str, request: Request):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    agent_api_url = job["agent_api_url"]
    url = f"{agent_api_url}/{tool}/{action}"
    # Forward method, headers, and body
    try:
        if request.method == "GET":
            resp = requests.get(url, params=dict(request.query_params), headers=request.headers)
        else:
            resp = requests.request(
                method=request.method,
                url=url,
                headers={k: v for k, v in request.headers.items() if k.lower() != 'host'},
                params=dict(request.query_params),
                data=await request.body(),
            )
        return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy error: {e}")

@app.get("/health")
def health():
    return {"status": "ok"}