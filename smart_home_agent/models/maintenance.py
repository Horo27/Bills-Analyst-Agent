"""
Maintenance task model
"""
from sqlalchemy import Column, String, Numeric, Date, Text, Boolean, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import BaseModel


class MaintenanceStatus(PyEnum):
    """Maintenance task status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class MaintenancePriority(PyEnum):
    """Maintenance task priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class MaintenanceTask(BaseModel):
    """Maintenance task model"""
    __tablename__ = "maintenance_tasks"

    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    estimated_cost = Column(Numeric(10, 2))
    actual_cost = Column(Numeric(10, 2))
    scheduled_date = Column(Date, index=True)
    completed_date = Column(Date)

    # Status and priority
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.SCHEDULED, index=True)
    priority = Column(Enum(MaintenancePriority), default=MaintenancePriority.MEDIUM)

    # Categorization
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    # Additional fields
    contractor = Column(String(200))
    contractor_phone = Column(String(20))
    contractor_email = Column(String(100))
    warranty_info = Column(Text)
    recurring_interval_months = Column(Integer)  # For recurring maintenance
    is_recurring = Column(Boolean, default=False)
    parent_task_id = Column(Integer, ForeignKey("maintenance_tasks.id"))  # For recurring tasks

    # Relationships
    category = relationship("Category", back_populates="maintenance_tasks")
    child_tasks = relationship("MaintenanceTask", remote_side=[parent_task_id])

    def __repr__(self):
        return f"<MaintenanceTask(title='{self.title}', status='{self.status}')>"

    @property
    def estimated_cost_float(self) -> float:
        """Return estimated cost as float"""
        return float(self.estimated_cost) if self.estimated_cost else 0.0

    @property
    def actual_cost_float(self) -> float:
        """Return actual cost as float"""
        return float(self.actual_cost) if self.actual_cost else 0.0
