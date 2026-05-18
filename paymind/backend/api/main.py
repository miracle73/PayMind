"""FastAPI application for PayMind agent."""
import os
import json
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, AsyncGenerator

from dotenv import load_dotenv
load_dotenv()

from agent.graph import agent_graph
from agent.state import AgentState
from agent.nodes import execute_task, generate_invoice, settle_payment, post_attestation


app = FastAPI(
    title="PayMind API",
    description="Autonomous AI agent that executes tasks, generates invoices, and settles payments",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskRequest(BaseModel):
    task: str
    wallet_address: str


class TaskResponse(BaseModel):
    session_id: str
    output: str
    invoice: Dict[str, Any]
    tx_hash: str
    attestation_hash: str
    status: str


@app.get("/")
async def root():
    return {"message": "PayMind Agent API", "status": "online"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/run-agent", response_model=TaskResponse)
async def run_agent(request: TaskRequest):
    """Run the full agent pipeline and return the final result."""
    session_id = str(uuid.uuid4())[:8]
    state: AgentState = {
        "task_input": request.task,
        "task_output": None,
        "invoice": None,
        "payment_tx": None,
        "attestation_hash": None,
        "status": "executing",
    }

    try:
        state = await execute_task(state)
        state = await generate_invoice(state)
        state = await settle_payment(state)
        state = await post_attestation(state)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "status": state["status"],
                "partial_state": {
                    "task_output": state.get("task_output"),
                    "invoice": state.get("invoice"),
                    "payment_tx": state.get("payment_tx"),
                },
            },
        )

    if state["status"] != "completed":
        raise HTTPException(status_code=500, detail=f"Agent failed. Status: {state['status']}")

    return TaskResponse(
        session_id=session_id,
        output=state["task_output"] or "",
        invoice=state["invoice"] or {},
        tx_hash=state["payment_tx"] or "",
        attestation_hash=state["attestation_hash"] or "",
        status="completed",
    )


@app.post("/run-agent-stream")
async def run_agent_stream(request: TaskRequest):
    """Run the agent pipeline with Server-Sent Events for live step updates."""

    async def event_stream() -> AsyncGenerator[str, None]:
        def emit(event: str, data: dict) -> str:
            return f"event: {event}\ndata: {json.dumps(data)}\n\n"

        state: AgentState = {
            "task_input": request.task,
            "task_output": None,
            "invoice": None,
            "payment_tx": None,
            "attestation_hash": None,
            "status": "executing",
        }

        yield emit("status", {"step": "executing", "message": "Executing task via LLM..."})
        try:
            state = await execute_task(state)
        except Exception as e:
            yield emit("error", {"step": "executing", "message": str(e)})
            return

        yield emit("status", {"step": "invoicing", "message": "Generating invoice..."})
        try:
            state = await generate_invoice(state)
        except Exception as e:
            yield emit("error", {"step": "invoicing", "message": str(e)})
            return

        yield emit("status", {"step": "paying", "message": "Settling payment on Kite chain..."})
        try:
            state = await settle_payment(state)
        except Exception as e:
            yield emit("error", {"step": "paying", "message": str(e)})
            return

        yield emit("status", {"step": "attesting", "message": "Posting on-chain attestation..."})
        try:
            state = await post_attestation(state)
        except Exception as e:
            yield emit("error", {"step": "attesting", "message": str(e)})
            return

        yield emit(
            "complete",
            {
                "step": "completed",
                "output": state["task_output"] or "",
                "invoice": state["invoice"] or {},
                "tx_hash": state["payment_tx"] or "",
                "attestation_hash": state["attestation_hash"] or "",
                "status": "completed",
            },
        )

    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
