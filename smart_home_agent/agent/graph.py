"""
LangGraph workflow orchestration for the Smart Home Agent
"""
from langgraph.graph import StateGraph, END, START
from typing import Literal
import logging

from .state import AgentState
from .nodes import (
    input_node,
    add_bill_node,
    query_expenses_node,
    get_summary_node,
    list_upcoming_node,
    get_statistics_node,
    response_node
)

logger = logging.getLogger(__name__)


def determine_action(state: AgentState) -> Literal["add_bill", "query_expenses", "get_summary", "list_upcoming", "get_statistics", "response"]:
    """Determine which action node to execute based on intent"""
    intent = state.get("current_intent")

    if intent == "add_bill":
        return "add_bill"
    elif intent == "query_expenses":
        return "query_expenses"
    elif intent == "get_summary":
        return "get_summary"
    elif intent == "list_upcoming":
        return "list_upcoming"
    elif intent == "get_statistics":
        return "get_statistics"
    else:
        # For greetings, general questions, or unrecognized intents
        return "response"


class SmartHomeAgent:
    """Main agent class that orchestrates the workflow"""

    def __init__(self):
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        # Initialize the graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("input", input_node)
        workflow.add_node("add_bill", add_bill_node)
        workflow.add_node("query_expenses", query_expenses_node)
        workflow.add_node("get_summary", get_summary_node)
        workflow.add_node("list_upcoming", list_upcoming_node)
        workflow.add_node("get_statistics", get_statistics_node)
        workflow.add_node("response", response_node)

        # Set entry point
        workflow.set_entry_point("input")

        # Add conditional edges from input to action nodes
        workflow.add_conditional_edges(
            "input",
            determine_action,
            {
                "add_bill": "add_bill",
                "query_expenses": "query_expenses",
                "get_summary": "get_summary",
                "list_upcoming": "list_upcoming",
                "get_statistics": "get_statistics",
                "response": "response"
            }
        )

        # All action nodes lead to response
        workflow.add_edge("add_bill", "response")
        workflow.add_edge("query_expenses", "response")
        workflow.add_edge("get_summary", "response")
        workflow.add_edge("list_upcoming", "response")
        workflow.add_edge("get_statistics", "response")

        # Response is the end
        workflow.add_edge("response", END)

        # Compile the graph
        return workflow.compile()

    async def process_message(self, message: str, session_id: str, user_id: str = None) -> dict:
        """Process a user message and return the response"""
        try:
            from langchain_core.messages import HumanMessage
            from .state import session_manager

            # Get or create session
            state = session_manager.get_session(session_id)
            if state is None:
                state = session_manager.create_session(session_id, user_id)

            # Add user message to state
            human_message = HumanMessage(content=message)
            state["messages"].append(human_message)

            # Process through the graph
            result = await self.graph.ainvoke(state)

            # Update session
            session_manager.update_session(session_id, result)

            # Return the response
            ai_response = result["messages"][-1].content

            return {
                "response": ai_response,
                "intent": result.get("current_intent"),
                "action_successful": result.get("action_successful", True),
                "session_id": session_id,
                "conversation_step": result.get("conversation_step", 0)
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again.",
                "intent": "error",
                "action_successful": False,
                "session_id": session_id,
                "error": str(e)
            }

    async def get_session_history(self, session_id: str) -> list:
        """Get conversation history for a session"""
        from .state import session_manager

        state = session_manager.get_session(session_id)
        if state is None:
            return []

        history = []
        for message in state["messages"]:
            history.append({
                "type": "human" if message.__class__.__name__ == "HumanMessage" else "ai",
                "content": message.content,
                "timestamp": getattr(message, "timestamp", None)
            })

        return history

    def clear_session(self, session_id: str):
        """Clear session data"""
        from .state import session_manager
        session_manager.clear_session(session_id)


# Global agent instance
smart_home_agent = SmartHomeAgent()
