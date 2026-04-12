"""Async node functions for PayMind agent workflow."""
import os
import httpx
from typing import Dict, Any
from .state import AgentState


# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")


async def execute_task(state: AgentState) -> AgentState:
    """
    Execute the task using OpenRouter API.
    Updates state with task_output and changes status to 'invoicing'.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": [
                        {"role": "user", "content": state["task_input"]}
                    ],
                },
                timeout=300.0,
            )
            response.raise_for_status()
            result = response.json()

            # Extract usage metrics for invoicing
            usage = result.get("usage", {})
            state["task_output"] = result["choices"][0]["message"]["content"]
            state["invoice"] = {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "model": result.get("model", OPENROUTER_MODEL),
            }
            state["status"] = "invoicing"

    except Exception as e:
        state["status"] = "error"
        state["task_output"] = f"Task execution failed: {str(e)}"
        raise

    return state


async def generate_invoice(state: AgentState) -> AgentState:
    """
    Generate invoice based on token usage.
    In a production system, this would calculate actual costs.
    For now, we'll use a simple formula and proceed to payment.
    """
    try:
        invoice = state.get("invoice", {})
        total_tokens = invoice.get("total_tokens", 0)

        # Simple cost calculation (example: $0.01 per 1K tokens)
        # In production, fetch real pricing from OpenRouter API
        cost_per_token = 0.00001  # $0.01 per 1000 tokens
        amount_wei = int(total_tokens * cost_per_token * 1e18)  # Convert to wei

        state["invoice"]["amount_wei"] = amount_wei
        state["invoice"]["cost_usd"] = float(amount_wei) / 1e18
        state["status"] = "paying"

    except Exception as e:
        state["status"] = "error"
        raise

    return state


async def settle_payment(state: AgentState) -> AgentState:
    """
    Settle payment on Kite chain using web3.py.
    Updates state with payment transaction hash.
    """
    try:
        from kite.client import KiteClient

        kite_client = KiteClient()
        amount_wei = state["invoice"]["amount_wei"]
        recipient_address = os.getenv("PAYMENT_RECIPIENT_ADDRESS")

        if not recipient_address:
            raise ValueError("PAYMENT_RECIPIENT_ADDRESS environment variable not set")

        tx_hash = kite_client.send_payment(
            to=recipient_address,
            amount_wei=amount_wei
        )
        state["payment_tx"] = tx_hash
        state["status"] = "attesting"

    except Exception as e:
        state["status"] = "error"
        raise

    return state


async def post_attestation(state: AgentState) -> AgentState:
    """
    Post attestation on Kite chain as proof of completion.
    Creates hash of task output, invoice, and payment tx.
    """
    try:
        from kite.client import KiteClient

        kite_client = KiteClient()

        # Create attestation data hash
        import hashlib
        import json

        attestation_data = {
            "task_hash": hashlib.sha256(state["task_input"].encode()).hexdigest(),
            "output_hash": hashlib.sha256(state["task_output"].encode()).hexdigest() if state["task_output"] else "",
            "invoice": state["invoice"],
            "payment_tx": state["payment_tx"],
        }
        data_hash = hashlib.sha256(json.dumps(attestation_data, sort_keys=True).encode()).hexdigest()

        # Post attestation on-chain
        tx_hash = kite_client.post_attestation(data_hash)
        state["attestation_hash"] = tx_hash
        state["status"] = "completed"

    except Exception as e:
        state["status"] = "error"
        raise

    return state
