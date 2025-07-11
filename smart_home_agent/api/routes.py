"""
FastAPI routes for the Smart Home Agent API
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import uuid
from datetime import date

from smart_home_agent.core.database import get_db
from smart_home_agent.services.expense_service import ExpenseService
from smart_home_agent.services.analytics_service import AnalyticsService
from smart_home_agent.agent import smart_home_agent
from .schemas import (
    CreateBillRequest,
    UpdateBillRequest,
    AgentQueryRequest,
    QueryBillsRequest,
    BillResponse,
    AgentResponse,
    SummaryResponse,
    StatsResponse,
    CategoryResponse,
    ErrorResponse,
    SuccessResponse
)

logger = logging.getLogger(__name__)

# Create main API router
api_router = APIRouter()

# Agent endpoints
agent_router = APIRouter(prefix="/agent", tags=["Agent"])
bills_router = APIRouter(prefix="/bills", tags=["Bills"])
analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])
categories_router = APIRouter(prefix="/categories", tags=["Categories"])


@agent_router.post("/chat", response_model=AgentResponse)
async def chat_with_agent(
    request: AgentQueryRequest,
    http_request: Request
):
    """Chat with the Smart Home Agent"""
    try:
        # Get or generate session ID
        session_id = request.session_id or getattr(http_request.state, "session_id", str(uuid.uuid4()))

        # Process message through agent
        result = await smart_home_agent.process_message(
            message=request.message,
            session_id=session_id,
            user_id=request.user_id
        )

        return AgentResponse(**result)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message")


@agent_router.get("/history/{session_id}")
async def get_conversation_history(session_id: str):
    """Get conversation history for a session"""
    try:
        history = await smart_home_agent.get_session_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation history")


@agent_router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear agent session data"""
    try:
        smart_home_agent.clear_session(session_id)
        return SuccessResponse(message="Session cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear session")


@bills_router.post("/", response_model=BillResponse)
async def create_bill(
    bill_data: CreateBillRequest,
    db: Session = Depends(get_db)
):
    """Create a new bill"""
    try:
        expense_service = ExpenseService(db)

        # Get or create category
        category = expense_service.get_or_create_category(bill_data.category_name)

        # Prepare bill data
        bill_dict = bill_data.dict(exclude={"category_name"})
        bill_dict["category_id"] = category.id

        # Create bill
        bill = expense_service.create_bill(bill_dict)

        return BillResponse.from_orm(bill)

    except Exception as e:
        print(f"Error creating bill: {bill_dict}")
        logger.error(f"Error creating bill: {e}")
        raise HTTPException(status_code=500, detail="Failed to create bill")


@bills_router.get("/", response_model=List[BillResponse])
async def get_bills(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    due_date_from: Optional[date] = Query(None),
    due_date_to: Optional[date] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get bills with optional filtering"""
    try:
        expense_service = ExpenseService(db)

        # Build filters
        filters = {}
        if category:
            filters["category"] = category
        if status:
            filters["status"] = status
        if min_amount is not None:
            filters["min_amount"] = min_amount
        if max_amount is not None:
            filters["max_amount"] = max_amount
        if due_date_from:
            filters["due_date_from"] = due_date_from
        if due_date_to:
            filters["due_date_to"] = due_date_to

        bills = expense_service.query_bills(filters)

        # Apply pagination
        paginated_bills = bills[offset:offset + limit]

        return [BillResponse.from_orm(bill) for bill in paginated_bills]

    except Exception as e:
        logger.error(f"Error getting bills: {e}")
        raise HTTPException(status_code=500, detail="Failed to get bills")


@bills_router.get("/{bill_id}", response_model=BillResponse)
async def get_bill(bill_id: int, db: Session = Depends(get_db)):
    """Get a specific bill by ID"""
    try:
        expense_service = ExpenseService(db)
        bill = expense_service.get_bill_by_id(bill_id)

        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")

        return BillResponse.from_orm(bill)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bill: {e}")
        raise HTTPException(status_code=500, detail="Failed to get bill")


@bills_router.put("/{bill_id}", response_model=BillResponse)
async def update_bill(
    bill_id: int,
    bill_data: UpdateBillRequest,
    db: Session = Depends(get_db)
):
    """Update an existing bill"""
    try:
        expense_service = ExpenseService(db)

        # Prepare update data
        update_dict = bill_data.dict(exclude_unset=True, exclude={"category_name"})

        # Handle category update
        if bill_data.category_name:
            category = expense_service.get_or_create_category(bill_data.category_name)
            update_dict["category_id"] = category.id

        # Update bill
        bill = expense_service.update_bill(bill_id, update_dict)

        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")

        return BillResponse.from_orm(bill)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating bill: {e}")
        raise HTTPException(status_code=500, detail="Failed to update bill")


@bills_router.delete("/{bill_id}")
async def delete_bill(bill_id: int, db: Session = Depends(get_db)):
    """Delete a bill"""
    try:
        expense_service = ExpenseService(db)
        success = expense_service.delete_bill(bill_id)

        if not success:
            raise HTTPException(status_code=404, detail="Bill not found")

        return SuccessResponse(message="Bill deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting bill: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete bill")


@bills_router.get("/upcoming/list")
async def get_upcoming_bills(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get upcoming bills"""
    try:
        expense_service = ExpenseService(db)
        bills = expense_service.get_upcoming_bills(days)

        return {
            "upcoming_bills": [BillResponse.from_orm(bill) for bill in bills],
            "count": len(bills),
            "days_ahead": days
        }

    except Exception as e:
        logger.error(f"Error getting upcoming bills: {e}")
        raise HTTPException(status_code=500, detail="Failed to get upcoming bills")


@bills_router.get("/overdue/list")
async def get_overdue_bills(db: Session = Depends(get_db)):
    """Get overdue bills"""
    try:
        expense_service = ExpenseService(db)
        bills = expense_service.get_overdue_bills()

        return {
            "overdue_bills": [BillResponse.from_orm(bill) for bill in bills],
            "count": len(bills)
        }

    except Exception as e:
        logger.error(f"Error getting overdue bills: {e}")
        raise HTTPException(status_code=500, detail="Failed to get overdue bills")


@analytics_router.get("/summary", response_model=SummaryResponse)
async def get_monthly_summary(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get monthly expense summary"""
    try:
        analytics_service = AnalyticsService(db)
        summary = analytics_service.get_monthly_summary(year, month)

        return SummaryResponse(**summary)

    except Exception as e:
        logger.error(f"Error getting monthly summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get monthly summary")


@analytics_router.get("/stats", response_model=StatsResponse)
async def get_comprehensive_stats(db: Session = Depends(get_db)):
    """Get comprehensive statistics"""
    try:
        analytics_service = AnalyticsService(db)
        stats = analytics_service.get_comprehensive_stats()

        return StatsResponse(**stats)

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@analytics_router.get("/categories/analysis")
async def get_category_analysis(db: Session = Depends(get_db)):
    """Get category-wise analysis"""
    try:
        analytics_service = AnalyticsService(db)
        analysis = analytics_service.get_category_analysis()

        return analysis

    except Exception as e:
        logger.error(f"Error getting category analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to get category analysis")


@analytics_router.get("/trends")
async def get_trend_analysis(
    months: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db)
):
    """Get spending trend analysis"""
    try:
        analytics_service = AnalyticsService(db)
        trends = analytics_service.get_trend_analysis(months)

        return trends

    except Exception as e:
        logger.error(f"Error getting trend analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trend analysis")


@categories_router.get("/", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    try:
        expense_service = ExpenseService(db)
        categories = expense_service.get_all_categories()

        return [CategoryResponse.from_orm(category) for category in categories]

    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get categories")


# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Smart Home Agent API"}


# Include all routers
api_router.include_router(agent_router)
api_router.include_router(bills_router)
api_router.include_router(analytics_router)
api_router.include_router(categories_router)
