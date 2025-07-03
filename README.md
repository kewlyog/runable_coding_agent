# Runable Coding Agent

A scalable, secure coding agent with sandboxing, orchestration, and advanced context management.

## Features
- **Shell**: Secure shell command execution
- **Code Execution**: Run Python/TypeScript with context
- **xdot**: GUI automation
- **Filesystem**: Secure file operations
- **Context Management**: Handles >1M tokens with pruning and LLM summarization
- **Orchestration Layer**: Schedule and manage agent jobs
- **Live VNC/Jupyter**: View and interact with the agent container

---

## Prerequisites
- Docker (for containerized setup)
- Python 3.8+ (for local dev)
- Node.js & npm (for optional React UI)

---

## Quick Start (Docker)

1. **Clone the repo:**
   ```sh
   git clone https://github.com/kewlyog/runable_coding_agent.git
   cd runable_coding_agent
   ```

2. **Set up environment:**
   - Create a `.env` file in root folder with:
     ```
     AGENT_API_KEY=your-strong-api-key
     OPENAI_API_KEY=sk-... (if using LLM context pruning)
     ```

3. **Build and run the agent container:**
   ```sh
   docker build -t coding-agent -f agent/Dockerfile .
   docker run -it -p 5001:5001 -p 6080:6080 -p 5901:5901 -p 8888:8888 --env-file agent/.env coding-agent
   ```
   - Access noVNC at: [http://localhost:6080](http://localhost:6080)
   - Access Jupyter at: [http://localhost:8888](http://localhost:8888)

4. **(Optional) Build and run orchestration server:**
   ```sh
   docker build -t orchestration -f orchestration/Dockerfile .
   docker run -it -p 5100:5100 --env-file orchestration/.env orchestration
   ```
   - Or run locally (see below)

---

## Local Development

1. **Install Python dependencies:**
   ```sh
   cd agent
   pip install -r requirements.txt
   cd ../orchestration
   pip install -r requirements.txt
   ```

2. **Start the agent API:**
   ```sh
   cd agent
   uvicorn main:app --host 0.0.0.0 --port 5001
   ```

3. **Start the orchestration API:**
   ```sh
   cd orchestration
   uvicorn api:app --host 0.0.0.0 --port 5100
   ```

---

## API Usage

- **Agent API:** [http://localhost:5001/docs](http://localhost:5001/docs)
- **Orchestration API:** [http://localhost:5100/docs](http://localhost:5100/docs)

All endpoints require the `X-API-Key` header with your API key.

---

## React UI (Optional)

1. **Set up UI:**
   ```sh
   cd agent-ui
   npm install
   npm run dev
   ```
   - Access at [http://localhost:5173](http://localhost:5173)

2. **CORS:**
   - Ensure CORS is enabled in your orchestration FastAPI app for browser access.

---

## How to test from UI

   To test your app from the UI, you need to have three main services running:

   1. Agent API (in Docker)
   This is the core agent that executes code, shell commands, manages context, etc.
   Run this in Docker (so /home/agent and all dependencies are available):
   ```sh
   docker build -t runable-agent .
   docker run --rm -it -p 5001:5001 -v $(pwd)/.env:/home/agent/.env runable-agent
   ```
   This exposes the agent API at http://localhost:5001

   2. Orchestration API (on your Mac)
   This is the FastAPI server that the UI talks to. It schedules jobs, proxies requests to the agent, and manages job state.
   Run this from your project root (not inside Docker):
   ```sh
   uvicorn orchestration.api:app --host 0.0.0.0 --port 5100
   ```
   This exposes the orchestration API at http://localhost:5100

   3. Frontend UI (React app)
   This is the user interface for interacting with the system.
   Run this from the agent-ui directory:
   ```sh
   cd agent-ui
   npm install
   npm run dev
   ```

## Kubernetes

- See `k8s/agent-job.yaml` for a sample agent job spec.
- Adapt for your cluster and orchestration needs.

---

## Security Notes
- Use strong API keys and keep them secret.
- The agent runs code in a sandbox, but always review security for your use case.
- For production, use HTTPS and restrict CORS origins.

---

## License
MIT (or your chosen license)

## Directory Structure & Codebase Layout

```
runable_coding_agent/
│
├── agent/                  # Agent container code
│   ├── api/                # REST API for tools (shell, code, xdot, fs)
│   │   ├── shell.py
│   │   ├── code.py
│   │   ├── xdot.py
│   │   └── fs.py
│   ├── context/            # Context management (pruning, chunking, recall)
│   │   └── context_manager.py
│   ├── kernels/            # Jupyter kernels, code execution logic
│   ├── utils/              # Shared utilities
│   ├── main.py             # Entrypoint for agent API
│   └── requirements.txt    # Python dependencies
│
├── orchestration/          # Orchestration server (FastAPI)
│   ├── jobs/               # Job management, Firecracker integration
│   ├── api.py              # FastAPI endpoints (/schedule, /status/:id)
│   ├── vm_launcher.py      # Firecracker VM launch logic
│   └── requirements.txt    # Python dependencies
│
├── Dockerfile              # Agent container Dockerfile
├── supervisord.conf        # Supervisor config for agent container
├── firecracker/            # Firecracker VM config/scripts
│   └── agent_vm_template.json
│
├── k8s/                    # (Bonus) Kubernetes/Nomad job specs
│   └── agent-job.yaml
│
└── README.md               # Project documentation
```

**Notes:**
- `agent/` is self-contained and can be built as a Docker image.
- `orchestration/` runs outside the VM/container, manages jobs and VMs.
- `firecracker/` holds configs/scripts for VM isolation.
- `k8s/` is optional for scaling in Kubernetes/Nomad. 