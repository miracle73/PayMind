"""Agent state schema for PayMind."""
from typing import TypedDict, Optional, Dict, Any


class AgentState(TypedDict):
    """State schema for the PayMind agent workflow."""
    task_input: str
    task_output: Optional[str]
    invoice: Optional[Dict[str, Any]]
    payment_tx: Optional[str]
    attestation_hash: Optional[str]
    status: str  # "pending", "executing", "invoicing", "paying", "attesting", "completed", "error"
