# Runable Coding Agent

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