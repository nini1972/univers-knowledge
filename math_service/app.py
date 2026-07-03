import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Ensure uvicorn runs can import local modules
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from math_agent import solve_math_derivation
except ImportError:
    from math_service.math_agent import solve_math_derivation

app = FastAPI(
    title="AstralBridge Math Agent Service",
    description="Microservice providing mathematical proof and derivation verification using agentic computational solvers.",
    version="1.0.0"
)

class DerivationRequest(BaseModel):
    concept: str
    equations: list[str]

class DerivationResponse(BaseModel):
    status: str
    concept: str
    proof_report: str

@app.get("/")
def read_root():
    return {"service": "AstralBridge Math Agent Service", "status": "active"}

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
