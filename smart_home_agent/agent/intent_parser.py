"""
Natural language intent recognition and entity extraction
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import logging
from smart_home_agent.core.config import settings


logger = logging.getLogger(__name__)


class IntentClassification(BaseModel):
    """Intent classification result"""
    intent: str = Field(description="The main intent of the user query")
    confidence: float = Field(description="Confidence score between 0 and 1")
    entities: Dict[str, Any] = Field(description="Extracted entities from the query")


class IntentParser:
    """Parse user intents and extract entities"""

    SUPPORTED_INTENTS = [
        "add_bill",
        "query_expenses", 
        "get_summary",
        "list_upcoming",
        "get_statistics",
        "update_bill",
        "delete_bill",
        "add_maintenance",
        "query_maintenance",
        "general_question",
        "greeting"
    ]

    def __init__(self, model_name: str = settings.AGENT_MODEL):
        print(f"Using model: {model_name}")
        self.llm = ChatOpenAI(
            openai_api_key=settings.OPENROUTER_API_KEY,  
            model_name='deepseek/deepseek-r1:free',
            openai_api_base="https://openrouter.ai/api/v1",
        )
        self.classification_prompt = ChatPromptTemplate.from_template("""
You are an expert at understanding user intents for a home expense and maintenance management system.

Analyze the user's message and classify it into one of these intents:
- add_bill: User wants to add a new bill or expense
- query_expenses: User wants to search or list existing bills/expenses
- get_summary: User wants a summary of their expenses
- list_upcoming: User wants to see upcoming bills
- get_statistics: User wants statistics or analytics
- update_bill: User wants to modify an existing bill
- delete_bill: User wants to remove a bill
- add_maintenance: User wants to add a maintenance task
- query_maintenance: User wants to search maintenance tasks
- general_question: General questions about expenses or maintenance
- greeting: User is greeting or saying hello

Also extract relevant entities like:
- amount: monetary values
- date: dates mentioned
- category: expense categories (utilities, subscriptions, maintenance, etc.)
- bill_name: name of bills or expenses
- frequency: how often something occurs

User message: {message}

Respond with the intent, confidence (0-1), and extracted entities.
""")

    async def parse_intent(self, message: str) -> IntentClassification:
        """Parse intent from user message"""
        try:
            # Use LLM for intent classification
            response = await self.llm.ainvoke(
                self.classification_prompt.format_messages(message=message)
            )

            # Parse the response (simplified - in practice you'd use structured output)
            intent, confidence, entities = self._parse_llm_response(response.content)

            # Enhance with regex-based entity extraction
            enhanced_entities = self._extract_entities_regex(message)
            entities.update(enhanced_entities)

            return IntentClassification(
                intent=intent,
                confidence=confidence,
                entities=entities
            )

        except Exception as e:
            logger.error(f"Intent parsing failed: {e}")
            return IntentClassification(
                intent="general_question",
                confidence=0.5,
                entities={}
            )

    def _parse_llm_response(self, response: str) -> Tuple[str, float, Dict[str, Any]]:
        """Parse LLM response (simplified implementation)"""
        # This is a simplified parser - in practice you'd use structured output
        intent = "general_question"
        confidence = 0.8
        entities = {}

        response_lower = response.lower()

        # Simple intent detection
        if any(word in response_lower for word in ["add", "create", "new bill"]):
            intent = "add_bill"
        elif any(word in response_lower for word in ["search", "find", "show", "list bills"]):
            intent = "query_expenses"
        elif any(word in response_lower for word in ["summary", "total", "overview"]):
            intent = "get_summary"
        elif any(word in response_lower for word in ["upcoming", "due", "next"]):
            intent = "list_upcoming"
        elif any(word in response_lower for word in ["statistics", "stats", "analytics"]):
            intent = "get_statistics"
        elif any(word in response_lower for word in ["hello", "hi", "hey"]):
            intent = "greeting"

        return intent, confidence, entities

    def _extract_entities_regex(self, message: str) -> Dict[str, Any]:
        """Extract entities using regex patterns"""
        entities = {}

        # Extract monetary amounts
        money_pattern = r'\$?(\d+(?:\.\d{2})?)'
        money_matches = re.findall(money_pattern, message)
        if money_matches:
            entities['amount'] = float(money_matches[0])

        # Extract dates (simple patterns)
        date_patterns = [
            r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
            r'(\d{4}-\d{1,2}-\d{1,2})',   # YYYY-MM-DD
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}',
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, message.lower())
            if matches:
                entities['date'] = matches[0]
                break

        # Extract categories
        categories = [
            'utilities', 'subscriptions', 'maintenance', 'insurance', 
            'rent', 'mortgage', 'internet', 'electricity', 'gas', 'water'
        ]

        message_lower = message.lower()
        for category in categories:
            if category in message_lower:
                entities['category'] = category.title()
                break

        return entities


# Global intent parser instance
intent_parser = IntentParser()
