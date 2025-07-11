"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


class BillStatusEnum(str, Enum):
    """Bill status options"""
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class BillFrequencyEnum(str, Enum):
    """Bill frequency options"""
    ONE_TIME = "ONE_TIME"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


# Request schemas
class CreateBillRequest(BaseModel):
    """Schema for creating a new bill"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    amount: float = Field(..., gt=0)
    due_date: date
    category_name: str = Field(..., min_length=1, max_length=100)
    vendor: Optional[str] = Field(None, max_length=200)
    account_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)
    is_recurring: bool = Field(default=False)
    frequency: BillFrequencyEnum = Field(default=BillFrequencyEnum.ONE_TIME)


class UpdateBillRequest(BaseModel):
    """Schema for updating a bill"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    amount: Optional[float] = Field(None, gt=0)
    due_date: Optional[date] = None
    category_name: Optional[str] = Field(None, min_length=1, max_length=100)
    vendor: Optional[str] = Field(None, max_length=200)
    account_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)
    status: Optional[BillStatusEnum] = None
    frequency: Optional[BillFrequencyEnum] = None


class AgentQueryRequest(BaseModel):
    """Schema for agent chat queries"""
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = Field(None, max_length=100)
    user_id: Optional[str] = Field(None, max_length=100)


class QueryBillsRequest(BaseModel):
    """Schema for querying bills"""
    category: Optional[str] = None
    status: Optional[BillStatusEnum] = None
    min_amount: Optional[float] = Field(None, ge=0)
    max_amount: Optional[float] = Field(None, ge=0)
    due_date_from: Optional[date] = None
    due_date_to: Optional[date] = None
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


# Response schemas
class CategoryResponse(BaseModel):
    """Schema for category response"""
    id: int
    name: str
    description: Optional[str]
    color: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BillResponse(BaseModel):
    """Schema for bill response"""
    id: int
    name: str
    description: Optional[str]
    amount: float
    due_date: date
    status: BillStatusEnum
    frequency: BillFrequencyEnum
    vendor: Optional[str]
    account_number: Optional[str]
    confirmation_number: Optional[str]
    notes: Optional[str]
    is_recurring: bool
    category: CategoryResponse
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentResponse(BaseModel):
    """Schema for agent response"""
    response: str
    intent: Optional[str]
    action_successful: bool
    session_id: str
    conversation_step: int
    timestamp: datetime = Field(default_factory=datetime.now)


class SummaryResponse(BaseModel):
    """Schema for expense summary response"""
    year: int
    month: int
    total_amount: float
    total_bills: int
    paid_bills: int
    pending_bills: int
    average_amount: float
    categories_count: int
    category_breakdown: Dict[str, float]
    top_category: Optional[str]


class StatsResponse(BaseModel):
    """Schema for comprehensive stats response"""
    current_month_total: float
    last_month_total: float
    average_monthly: float
    month_over_month_change: float
    top_category: str
    total_categories: int
    upcoming_bills_count: int
    overdue_bills_count: int
    current_month_bills: int
    payment_completion_rate: float


class PaginatedResponse(BaseModel):
    """Schema for paginated responses"""
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class SuccessResponse(BaseModel):
    """Schema for success responses"""
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)
