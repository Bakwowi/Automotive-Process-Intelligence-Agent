import sys
from pathlib import Path

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # Adjust parent index if needed
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))



from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from orchestrator.state import AgentState
from agents.nodes import (
    classify_node,
    research_node,
    validate_node,
    write_report_node,
    human_checkpoint_node,
    save_report_node
)



def route_after_human(state: AgentState) -> str:
    """
    Conditional edge after human checkpoint.
    Approved → save and end.
    Rejected → loop back to research (with feedback), max 3 iterations.
    """
    if state.get("human_approved"):
        return "save_report"

    if state.get("iteration_count", 0) >= 3:
        # Safety valve — prevent infinite loops
        return "save_report"

    return "research"   # Loop back with human_feedback in state


def build_graph():
    builder = StateGraph(AgentState)

    # Add all nodes
    builder.add_node("classify",         classify_node)
    builder.add_node("research",         research_node)
    builder.add_node("validate",         validate_node)
    builder.add_node("write_report",     write_report_node)
    builder.add_node("human_checkpoint", human_checkpoint_node)
    builder.add_node("save_report",      save_report_node)

    # Linear edges
    builder.add_edge(START,          "classify")
    builder.add_edge("classify",     "research")
    builder.add_edge("research",     "validate")
    builder.add_edge("validate",     "write_report")
    builder.add_edge("write_report", "human_checkpoint")

    # Conditional edge after human review
    builder.add_conditional_edges(
        "human_checkpoint",
        route_after_human,
        {
            "save_report": "save_report",
            "research":    "research"    # Loop: goes research → validate → write → checkpoint
        }
    )

    builder.add_edge("save_report", END)
    

    # MemorySaver enables human-in-the-loop via interrupt()
    checkpointer = MemorySaver()


    return builder.compile(checkpointer=checkpointer)


# Singleton graph
graph = build_graph()
# graph.get_graph().draw_mermaid_png(output_file_path="graph.png")