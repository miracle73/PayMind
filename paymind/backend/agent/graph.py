"""LangGraph StateGraph for PayMind agent."""
from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import execute_task, generate_invoice, settle_payment, post_attestation


def build_agent_graph() -> StateGraph:
    """
    Build and return the PayMind agent workflow graph.

    Flow:
    1. execute_task → 2. generate_invoice → 3. settle_payment → 4. post_attestation → END
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("execute_task", execute_task)
    workflow.add_node("generate_invoice", generate_invoice)
    workflow.add_node("settle_payment", settle_payment)
    workflow.add_node("post_attestation", post_attestation)

    # Define entry point
    workflow.set_entry_point("execute_task")

    # Add edges - linear workflow
    workflow.add_edge("execute_task", "generate_invoice")
    workflow.add_edge("generate_invoice", "settle_payment")
    workflow.add_edge("settle_payment", "post_attestation")
    workflow.add_edge("post_attestation", END)

    return workflow


# Compile the graph for use
agent_graph = build_agent_graph().compile()
