import os
import sys
import time
import uuid
import threading
import json
import urllib.request
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

# Ensure uvicorn runs can import local modules
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from math_agent import solve_math_derivation
except ImportError:
    from math_service.math_agent import solve_math_derivation

# --- AstralBridge SPECIFICATION ---
PORT = int(os.getenv("PORT", 4004))
BRIDGE_URL = os.getenv("BRIDGE_URL", "http://localhost:3001")
PUBLIC_URL = os.getenv("PUBLIC_URL", f"http://localhost:{PORT}")

agent_card = {
    "name": "MathAgent",
    "role": "Mathematical Proof Expert",
    "description": "Solves, verifies, and documents complex mathematical proofs and derivations using python/sympy code.",
    "capabilities": ["verify_derivation"],
    "skills": [
        {
            "id": "verify_derivation",
            "name": "Verify Derivation",
            "description": "Performs a formal mathematical verification and derivation check using SymPy.",
            "inputModes": ["text"],
            "outputModes": ["text"],
            "parameters": {
                "type": "object",
                "properties": {
                    "concept": {"type": "string"},
                    "equations": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["concept", "equations"]
            }
        }
    ],
    "endpoint": f"{PUBLIC_URL}/a2a",
    "status": "active",
    "framework": "FastAPI + CrewAI",
    "provider": "Local"
}

tasks: dict = {}
tasks_lock = threading.Lock()


class DerivationRequest(BaseModel):
    concept: str
    equations: list[str]


class DerivationResponse(BaseModel):
    status: str
    concept: str
    proof_report: str


class A2APayload(BaseModel):
    concept: str
    equations: list[str]

    @field_validator("equations")
    @classmethod
    def equations_must_be_strings(cls, v: list) -> list:
        if not all(isinstance(eq, str) for eq in v):
            raise ValueError("All equations must be strings")
        return v


class A2ATaskRequest(BaseModel):
    capability: str
    payload: A2APayload


# --- Background Registration and Heartbeat Loop ---
def background_registration_loop():
    time.sleep(3)  # Wait for FastAPI to bind
    card_json = json.dumps(agent_card).encode("utf-8")

    while True:
        try:
            req = urllib.request.Request(
                f"{BRIDGE_URL}/agents/register",
                data=card_json,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req):
                print("Registered with AstralBridge")
        except Exception as e:
            print(f"Registration failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)
            continue

        while True:
            try:
                heartbeat_data = json.dumps({"status": "active"}).encode("utf-8")
                req = urllib.request.Request(
                    f"{BRIDGE_URL}/agents/{agent_card['name']}/heartbeat",
                    data=heartbeat_data,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req):
                    pass
            except Exception as e:
                print(f"Heartbeat failed: {e}. Re-registering...")
                break
            time.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    t = threading.Thread(target=background_registration_loop, daemon=True)
    t.start()
    yield


app = FastAPI(
    title="AstralBridge Math Agent Service",
    description="Microservice providing mathematical proof and derivation verification using agentic computational solvers.",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def read_root():
    return {"service": "AstralBridge Math Agent Service", "status": "active"}


@app.get("/.well-known/agent-card.json")
def get_agent_card():
    return agent_card


@app.post("/verify-derivation", response_model=DerivationResponse)
def verify_derivation(payload: DerivationRequest):
    try:
        report = solve_math_derivation(payload.concept, payload.equations)
        return DerivationResponse(
            status="verified",
            concept=payload.concept,
            proof_report=report
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _execute_a2a_task(req: A2ATaskRequest) -> dict:
    """Shared execution logic for A2A task endpoints."""
    if req.capability != "verify_derivation":
        raise HTTPException(status_code=400, detail="Unsupported capability")

    task_id = str(uuid.uuid4())
    created_at = int(time.time() * 1000)

    try:
        report = solve_math_derivation(req.payload.concept, req.payload.equations)
        task = {
            "id": task_id,
            "status": "completed",
            "result": {"proof_report": report},
            "createdAt": created_at,
            "updatedAt": int(time.time() * 1000),
        }
    except Exception as e:
        task = {
            "id": task_id,
            "status": "failed",
            "result": {"error": str(e)},
            "createdAt": created_at,
            "updatedAt": int(time.time() * 1000),
        }

    with tasks_lock:
        tasks[task_id] = task
    return task


@app.post("/a2a/task")
def run_a2a_task(req: A2ATaskRequest):
    """A2A task endpoint. AstralBridge calls {agent.endpoint}/task = /a2a/task."""
    return _execute_a2a_task(req)


@app.get("/a2a/task/{task_id}")
def get_a2a_task(task_id: str):
    with tasks_lock:
        task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
