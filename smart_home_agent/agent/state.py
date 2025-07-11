"""
Agent state management for conversation context
"""
from typing import Dict, List, Any, Optional, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """State for the Smart Home Agent"""
    # Conversation messages
    messages: Annotated[List[BaseMessage], add_messages]

    # Current intent and context
    current_intent: Optional[str]
    extracted_entities: Dict[str, Any]

    # User context
    user_id: Optional[str]
    session_id: Optional[str]

    # Query results and working data
    query_results: List[Dict[str, Any]]
    summary_data: Dict[str, Any]

    # Action tracking
    last_action: Optional[str]
    action_successful: bool
    error_message: Optional[str]

    # Conversation context
    conversation_step: int
    needs_clarification: bool
    clarification_question: Optional[str]


class SessionManager:
    """Manage agent sessions and state persistence"""

    def __init__(self):
        self.sessions: Dict[str, AgentState] = {}

    def create_session(self, session_id: str, user_id: Optional[str] = None) -> AgentState:
        """Create a new agent session"""
        initial_state = AgentState(
            messages=[],
            current_intent=None,
            extracted_entities={},
            user_id=user_id,
            session_id=session_id,
            query_results=[],
            summary_data={},
            last_action=None,
            action_successful=True,
            error_message=None,
            conversation_step=0,
            needs_clarification=False,
            clarification_question=None
        )
        self.sessions[session_id] = initial_state
        return initial_state

    def get_session(self, session_id: str) -> Optional[AgentState]:
        """Get existing session state"""
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, state: AgentState):
        """Update session state"""
        self.sessions[session_id] = state

    def clear_session(self, session_id: str):
        """Clear session data"""
        if session_id in self.sessions:
            del self.sessions[session_id]


# Global session manager instance
session_manager = SessionManager()
