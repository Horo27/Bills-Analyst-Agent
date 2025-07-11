"""
Bill and expense models
"""
from sqlalchemy import Integer, Column, String, Numeric, Date, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from decimal import Decimal
from .base import BaseModel


class BillStatus(PyEnum):
    """Bill status enumeration"""
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class BillFrequency(PyEnum):
    """Bill frequency enumeration"""
    ONE_TIME = "ONE_TIME"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


class Bill(BaseModel):
    """Bill/Expense model"""
    __tablename__ = "bills"

    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    amount = Column(Numeric(10, 2), nullable=False)
    due_date = Column(Date, nullable=False, index=True)

    # Status and frequency
    status = Column(Enum(BillStatus), default=BillStatus.PENDING, index=True)
    frequency = Column(Enum(BillFrequency), default=BillFrequency.ONE_TIME)

    # Categorization
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    # Additional fields
    vendor = Column(String(200))
    account_number = Column(String(100))
    confirmation_number = Column(String(100))
    notes = Column(Text)
    is_recurring = Column(Boolean, default=False)

    # Relationships
    category = relationship("Category", back_populates="bills")

    def __repr__(self):
        return f"<Bill(name='{self.name}', amount={self.amount}, due_date='{self.due_date}')>"

    @property
    def amount_float(self) -> float:
        """Return amount as float"""
        return float(self.amount)

    @property
    def is_overdue(self) -> bool:
        """Check if bill is overdue"""
        from datetime import date
        return self.due_date < date.today() and self.status == BillStatus.PENDING
