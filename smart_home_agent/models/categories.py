"""
Category model for expense classification
"""
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class Category(BaseModel):
    """Category model for classifying expenses"""
    __tablename__ = "categories"

    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    color = Column(String(7), default="#3B82F6")  # Hex color code
    is_active = Column(Boolean, default=True)

    # Relationships
    bills = relationship("Bill", back_populates="category")
    maintenance_tasks = relationship("MaintenanceTask", back_populates="category")

    def __repr__(self):
        return f"<Category(name='{self.name}')>"
