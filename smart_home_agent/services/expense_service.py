"""
Service layer for expense and bill management
"""
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from smart_home_agent.models import Bill, Category, BillStatus, BillFrequency
import logging

logger = logging.getLogger(__name__)


class ExpenseService:
    """Service for managing expenses and bills"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create_bill(self, bill_data: Dict[str, Any]) -> Bill:
        """Create a new bill"""
        try:
            bill = Bill(**bill_data)
            self.db.add(bill)
            self.db.commit()
            self.db.refresh(bill)
            logger.info(f"Created bill: {bill.name}")
            return bill
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create bill: {e}")
            raise

    def get_bill_by_id(self, bill_id: int) -> Optional[Bill]:
        """Get bill by ID"""
        return self.db.query(Bill).filter(Bill.id == bill_id).first()

    def update_bill(self, bill_id: int, update_data: Dict[str, Any]) -> Optional[Bill]:
        """Update an existing bill"""
        try:
            bill = self.get_bill_by_id(bill_id)
            if not bill:
                return None

            for key, value in update_data.items():
                if hasattr(bill, key):
                    setattr(bill, key, value)

            self.db.commit()
            self.db.refresh(bill)
            logger.info(f"Updated bill: {bill.name}")
            return bill
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update bill: {e}")
            raise

    def delete_bill(self, bill_id: int) -> bool:
        """Delete a bill"""
        try:
            bill = self.get_bill_by_id(bill_id)
            if not bill:
                return False

            self.db.delete(bill)
            self.db.commit()
            logger.info(f"Deleted bill: {bill.name}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete bill: {e}")
            raise

    def query_bills(self, filters: Dict[str, Any] = None) -> List[Bill]:
        """Query bills with optional filters"""
        query = self.db.query(Bill)

        if filters:
            # Category filter
            if "category" in filters:
                category_name = filters["category"]
                query = query.join(Category).filter(Category.name.ilike(f"%{category_name}%"))

            # Date range filter
            if "date_range" in filters:
                date_filter = filters["date_range"]
                if isinstance(date_filter, str):
                    # Parse date string (simplified)
                    try:
                        filter_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
                        query = query.filter(Bill.due_date == filter_date)
                    except ValueError:
                        pass

            # Status filter
            if "status" in filters:
                query = query.filter(Bill.status == filters["status"])

            # Amount range filter
            if "min_amount" in filters:
                query = query.filter(Bill.amount >= filters["min_amount"])
            if "max_amount" in filters:
                query = query.filter(Bill.amount <= filters["max_amount"])

        return query.order_by(desc(Bill.due_date)).all()

    def get_upcoming_bills(self, days: int = 30) -> List[Bill]:
        """Get bills due in the next N days"""
        end_date = date.today() + timedelta(days=days)

        return self.db.query(Bill).filter(
            and_(
                Bill.due_date >= date.today(),
                Bill.due_date <= end_date,
                Bill.status == BillStatus.PENDING
            )
        ).order_by(asc(Bill.due_date)).all()

    def get_overdue_bills(self) -> List[Bill]:
        """Get overdue bills"""
        return self.db.query(Bill).filter(
            and_(
                Bill.due_date < date.today(),
                Bill.status == BillStatus.PENDING
            )
        ).order_by(asc(Bill.due_date)).all()

    def get_bills_by_category(self, category_name: str) -> List[Bill]:
        """Get bills by category name"""
        return self.db.query(Bill).join(Category).filter(
            Category.name.ilike(f"%{category_name}%")
        ).order_by(desc(Bill.due_date)).all()

    def get_or_create_category(self, name: str) -> Category:
        """Get existing category or create new one"""
        category = self.db.query(Category).filter(Category.name.ilike(name)).first()

        if not category:
            category = Category(name=name.title())
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            logger.info(f"Created new category: {name}")

        return category

    def get_all_categories(self) -> List[Category]:
        """Get all active categories"""
        return self.db.query(Category).filter(Category.is_active == True).all()

    def mark_bill_paid(self, bill_id: int) -> Optional[Bill]:
        """Mark a bill as paid"""
        return self.update_bill(bill_id, {"status": BillStatus.PAID})

    def get_monthly_bills(self, year: int, month: int) -> List[Bill]:
        """Get bills for a specific month"""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        return self.db.query(Bill).filter(
            and_(
                Bill.due_date >= start_date,
                Bill.due_date <= end_date
            )
        ).order_by(asc(Bill.due_date)).all()
