"""FastAPI application for PayMind agent."""
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uuid

from agent.graph import agent_graph
from agent.state import AgentState


app = FastAPI(
    title="PayMind API",
    description="Autonomous AI agent that executes tasks, generates invoices, and settles payments",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskRequest(BaseModel):
    """Request model for running the agent."""
    task: str
    wallet_address: str


class TaskResponse(BaseModel):
    """Response model for agent execution."""
    session_id: str
    output: str
    invoice: Dict[str, Any]
    tx_hash: str
    attestation_hash: str
    status: str


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "PayMind Agent API", "status": "online"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/run-agent", response_model=TaskResponse)
async def run_agent(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Run the PayMind agent with a given task.

    This endpoint executes the full workflow:
    1. Execute task via OpenRouter
    2. Generate invoice based on token usage
    3. Settle payment on Kite chain
    4. Post attestation on-chain

    Args:
        request: TaskRequest containing task string and wallet address

    Returns:
        TaskResponse with agent results
    """
    try:
        # Create initial state
        initial_state: AgentState = {
            "task_input": request.task,
            "task_output": None,
            "invoice": None,
            "payment_tx": None,
            "attestation_hash": None,
            "status": "executing",
        }

        # Run the graph synchronously (in production, use async graph execution)
        # For now, we'll execute each node sequentially with proper error handling
        from agent.nodes import (
            execute_task,
            generate_invoice,
            settle_payment,
            post_attestation
        )

        state = initial_state.copy()
        session_id = str(uuid.uuid4())[:8]

        try:
            # Step 1: Execute task
            state = await execute_task(state)

            # Step 2: Generate invoice
            state = await generate_invoice(state)

            # Step 3: Settle payment
            state = await settle_payment(state)

            # Step 4: Post attestation
            state = await post_attestation(state)

        except Exception as e:
            state["status"] = "error"
            raise HTTPException(
                status_code=500,
                detail={
                    "error": str(e),
                    "status": state["status"],
                    "partial_state": {
                        "task_output": state.get("task_output"),
                        "invoice": state.get("invoice"),
                        "payment_tx": state.get("payment_tx"),
                    }
                }
            )

        if state["status"] == "completed":
            return TaskResponse(
                session_id=session_id,
                output=state["task_output"] or "",
                invoice=state["invoice"] or {},
                tx_hash=state["payment_tx"] or "",
                attestation_hash=state["attestation_hash"] or "",
                status="completed"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Agent did not complete successfully. Status: {state['status']}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
