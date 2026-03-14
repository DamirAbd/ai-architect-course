from langgraph.graph import StateGraph, END

from state import TravelState
from rag import policy_rag_agent
from agents import (
    manager_extract_request,
    travel_search_agent,
    manager_build_shortlist,
    manager_wait_for_selection,
    route_after_selection,
    manager_check_approval,
    route_after_approval_check,
    manager_wait_for_approval,
    route_after_approval_wait,
    booking_agent,
    manager_build_final_answer,
)


def build_graph():
    workflow = StateGraph(TravelState)

    workflow.add_node("manager_extract_request", manager_extract_request)
    workflow.add_node("policy_rag_agent", policy_rag_agent)
    workflow.add_node("travel_search_agent", travel_search_agent)
    workflow.add_node("manager_build_shortlist", manager_build_shortlist)
    workflow.add_node("manager_wait_for_selection", manager_wait_for_selection)
    workflow.add_node("manager_check_approval", manager_check_approval)
    workflow.add_node("manager_wait_for_approval", manager_wait_for_approval)
    workflow.add_node("booking_agent", booking_agent)
    workflow.add_node("manager_build_final_answer", manager_build_final_answer)

    workflow.set_entry_point("manager_extract_request")

    workflow.add_edge("manager_extract_request", "policy_rag_agent")
    workflow.add_edge("policy_rag_agent", "travel_search_agent")
    workflow.add_edge("travel_search_agent", "manager_build_shortlist")
    workflow.add_edge("manager_build_shortlist", "manager_wait_for_selection")

    workflow.add_conditional_edges(
        "manager_wait_for_selection",
        route_after_selection,
        {
            "wait": END,
            "selected": "manager_check_approval",
        },
    )

    workflow.add_conditional_edges(
        "manager_check_approval",
        route_after_approval_check,
        {
            "approval_needed": "manager_wait_for_approval",
            "booking": "booking_agent",
        },
    )

    workflow.add_conditional_edges(
        "manager_wait_for_approval",
        route_after_approval_wait,
        {
            "wait": END,
            "booking": "booking_agent",
        },
    )

    workflow.add_edge("booking_agent", "manager_build_final_answer")
    workflow.add_edge("manager_build_final_answer", END)

    return workflow.compile()