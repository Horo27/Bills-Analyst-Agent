"""
LangGraph nodes for agent workflow
"""
from typing import Dict, Any
import logging
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from smart_home_agent.core.database import get_db, DatabaseManager
from smart_home_agent.models import Bill, Category, MaintenanceTask, BillStatus
from smart_home_agent.services.expense_service import ExpenseService
from smart_home_agent.services.analytics_service import AnalyticsService
from .state import AgentState
from .intent_parser import intent_parser

logger = logging.getLogger(__name__)


async def input_node(state: AgentState) -> AgentState:
    """Process user input and extract intent"""
    try:
        # Get the latest message
        if not state["messages"]:
            return state

        latest_message = state["messages"][-1]
        user_input = latest_message.content

        # Parse intent and entities
        classification = await intent_parser.parse_intent(user_input)

        # Update state
        state["current_intent"] = classification.intent
        state["extracted_entities"] = classification.entities
        state["conversation_step"] += 1
        state["needs_clarification"] = False

        logger.info(f"Parsed intent: {classification.intent} with entities: {classification.entities}")

        return state

    except Exception as e:
        logger.error(f"Error in input_node: {e}")
        state["error_message"] = str(e)
        state["action_successful"] = False
        return state


async def add_bill_node(state: AgentState) -> AgentState:
    """Handle adding a new bill"""
    try:
        entities = state["extracted_entities"]

        # Check if we have required information
        required_fields = ["amount"]
        missing_fields = [field for field in required_fields if field not in entities]

        if missing_fields:
            state["needs_clarification"] = True
            state["clarification_question"] = f"I need more information. Please provide: {', '.join(missing_fields)}"
            return state

        # Create bill with available information
        with DatabaseManager() as db:
            expense_service = ExpenseService(db)

            # Get or create category
            category_name = entities.get("category", "Other")
            category = expense_service.get_or_create_category(category_name)

            # Create bill
            bill_data = {
                "name": entities.get("bill_name", "New Bill"),
                "amount": entities["amount"],
                "due_date": entities.get("date", date.today() + timedelta(days=30)),
                "category_id": category.id,
                "description": entities.get("description", ""),
                "status": BillStatus.PENDING
            }

            new_bill = expense_service.create_bill(bill_data)

            state["query_results"] = [new_bill.to_dict()]
            state["action_successful"] = True
            state["last_action"] = "add_bill"

        return state

    except Exception as e:
        logger.error(f"Error in add_bill_node: {e}")
        state["error_message"] = str(e)
        state["action_successful"] = False
        return state


async def query_expenses_node(state: AgentState) -> AgentState:
    """Handle querying expenses"""
    try:
        entities = state["extracted_entities"]

        with DatabaseManager() as db:
            expense_service = ExpenseService(db)

            # Build query filters
            filters = {}
            if "category" in entities:
                filters["category"] = entities["category"]
            if "date" in entities:
                filters["date_range"] = entities["date"]

            # Query bills
            bills = expense_service.query_bills(filters)

            state["query_results"] = [bill.to_dict() for bill in bills]
            state["action_successful"] = True
            state["last_action"] = "query_expenses"

        return state

    except Exception as e:
        logger.error(f"Error in query_expenses_node: {e}")
        state["error_message"] = str(e)
        state["action_successful"] = False
        return state


async def get_summary_node(state: AgentState) -> AgentState:
    """Handle getting expense summary"""
    try:
        with DatabaseManager() as db:
            analytics_service = AnalyticsService(db)

            # Get monthly summary
            summary = analytics_service.get_monthly_summary()

            state["summary_data"] = summary
            state["action_successful"] = True
            state["last_action"] = "get_summary"

        return state

    except Exception as e:
        logger.error(f"Error in get_summary_node: {e}")
        state["error_message"] = str(e)
        state["action_successful"] = False
        return state


async def list_upcoming_node(state: AgentState) -> AgentState:
    """Handle listing upcoming bills"""
    try:
        with DatabaseManager() as db:
            expense_service = ExpenseService(db)

            # Get upcoming bills (next 30 days)
            upcoming_bills = expense_service.get_upcoming_bills(days=30)

            state["query_results"] = [bill.to_dict() for bill in upcoming_bills]
            state["action_successful"] = True
            state["last_action"] = "list_upcoming"

        return state

    except Exception as e:
        logger.error(f"Error in list_upcoming_node: {e}")
        state["error_message"] = str(e)
        state["action_successful"] = False
        return state


async def get_statistics_node(state: AgentState) -> AgentState:
    """Handle getting statistics"""
    try:
        with DatabaseManager() as db:
            analytics_service = AnalyticsService(db)

            # Get comprehensive statistics
            stats = analytics_service.get_comprehensive_stats()

            state["summary_data"] = stats
            state["action_successful"] = True
            state["last_action"] = "get_statistics"

        return state

    except Exception as e:
        logger.error(f"Error in get_statistics_node: {e}")
        state["error_message"] = str(e)
        state["action_successful"] = False
        return state


async def response_node(state: AgentState) -> AgentState:
    """Generate response based on the action taken"""
    try:
        from langchain_core.messages import AIMessage

        intent = state["current_intent"]
        action_successful = state["action_successful"]

        if not action_successful:
            error_msg = state.get("error_message", "An error occurred")
            response = f"I apologize, but I encountered an error: {error_msg}"
        elif state.get("needs_clarification"):
            response = state["clarification_question"]
        else:
            response = generate_response_for_intent(intent, state)

        # Add AI message to conversation
        ai_message = AIMessage(content=response)
        state["messages"].append(ai_message)

        return state

    except Exception as e:
        logger.error(f"Error in response_node: {e}")
        from langchain_core.messages import AIMessage
        error_response = AIMessage(content="I apologize, but I'm having trouble generating a response right now.")
        state["messages"].append(error_response)
        return state


def generate_response_for_intent(intent: str, state: AgentState) -> str:
    """Generate appropriate response based on intent"""
    if intent == "add_bill":
        if state["action_successful"]:
            bill_data = state["query_results"][0]
            return f"✅ Successfully added bill: {bill_data['name']} for ${bill_data['amount']} due on {bill_data['due_date']}"
        else:
            return "❌ Failed to add the bill. Please try again."

    elif intent == "query_expenses":
        results = state["query_results"]
        if results:
            response = f"Found {len(results)} bills:\n"
            for bill in results[:5]:  # Limit to 5 results
                response += f"• {bill['name']}: ${bill['amount']} due {bill['due_date']}\n"
            if len(results) > 5:
                response += f"... and {len(results) - 5} more"
            return response
        else:
            return "No bills found matching your criteria."

    elif intent == "get_summary":
        summary = state["summary_data"]
        return f"""📊 Monthly Summary:
• Total expenses: ${summary.get('total_amount', 0):.2f}
• Number of bills: {summary.get('total_bills', 0)}
• Categories: {summary.get('categories_count', 0)}
• Average bill amount: ${summary.get('average_amount', 0):.2f}"""

    elif intent == "list_upcoming":
        results = state["query_results"]
        if results:
            response = f"📅 Upcoming bills ({len(results)}):\n"
            for bill in results:
                response += f"• {bill['name']}: ${bill['amount']} due {bill['due_date']}\n"
            return response
        else:
            return "No upcoming bills found."

    elif intent == "get_statistics":
        stats = state["summary_data"]
        return f"""📈 Expense Statistics:
• This month: ${stats.get('current_month_total', 0):.2f}
• Last month: ${stats.get('last_month_total', 0):.2f}
• Average monthly: ${stats.get('average_monthly', 0):.2f}
• Top category: {stats.get('top_category', 'N/A')}"""

    elif intent == "greeting":
        return "Hello! I'm your Smart Home Expense & Maintenance Assistant. I can help you manage bills, track expenses, and schedule maintenance tasks. What would you like to do today?"

    else:
        return "I understand you have a question about your expenses or maintenance. Could you please be more specific about what you'd like to know?"
