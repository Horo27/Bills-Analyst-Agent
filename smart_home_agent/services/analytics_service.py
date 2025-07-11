"""
Service for analytics and reporting
"""
from typing import Dict, Any, List
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from decimal import Decimal

from smart_home_agent.models import Bill, Category, MaintenanceTask, BillStatus
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics and reporting"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_monthly_summary(self, year: int = None, month: int = None) -> Dict[str, Any]:
        """Get monthly expense summary"""
        if year is None:
            year = date.today().year
        if month is None:
            month = date.today().month

        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        # Get bills for the month
        bills = self.db.query(Bill).filter(
            and_(
                Bill.due_date >= start_date,
                Bill.due_date <= end_date
            )
        ).all()

        # Calculate statistics
        total_amount = sum(float(bill.amount) for bill in bills)
        total_bills = len(bills)
        paid_bills = len([b for b in bills if b.status == BillStatus.PAID])
        pending_bills = len([b for b in bills if b.status == BillStatus.PENDING])

        # Category breakdown
        category_totals = {}
        for bill in bills:
            category = bill.category.name
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += float(bill.amount)

        return {
            "year": year,
            "month": month,
            "total_amount": total_amount,
            "total_bills": total_bills,
            "paid_bills": paid_bills,
            "pending_bills": pending_bills,
            "average_amount": total_amount / total_bills if total_bills > 0 else 0,
            "categories_count": len(category_totals),
            "category_breakdown": category_totals,
            "top_category": max(category_totals.items(), key=lambda x: x[1])[0] if category_totals else None
        }

    def get_yearly_summary(self, year: int = None) -> Dict[str, Any]:
        """Get yearly expense summary"""
        if year is None:
            year = date.today().year

        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        bills = self.db.query(Bill).filter(
            and_(
                Bill.due_date >= start_date,
                Bill.due_date <= end_date
            )
        ).all()

        # Monthly breakdown
        monthly_totals = {}
        for bill in bills:
            month = bill.due_date.month
            if month not in monthly_totals:
                monthly_totals[month] = 0
            monthly_totals[month] += float(bill.amount)

        total_amount = sum(float(bill.amount) for bill in bills)

        return {
            "year": year,
            "total_amount": total_amount,
            "total_bills": len(bills),
            "average_monthly": total_amount / 12,
            "monthly_breakdown": monthly_totals,
            "highest_month": max(monthly_totals.items(), key=lambda x: x[1]) if monthly_totals else None,
            "lowest_month": min(monthly_totals.items(), key=lambda x: x[1]) if monthly_totals else None
        }

    def get_category_analysis(self) -> Dict[str, Any]:
        """Get category-wise analysis"""
        # Query category totals
        category_query = self.db.query(
            Category.name,
            func.sum(Bill.amount).label("total_amount"),
            func.count(Bill.id).label("bill_count"),
            func.avg(Bill.amount).label("average_amount")
        ).join(Bill).group_by(Category.name).all()

        categories = []
        for cat_name, total, count, avg in category_query:
            categories.append({
                "name": cat_name,
                "total_amount": float(total or 0),
                "bill_count": count or 0,
                "average_amount": float(avg or 0)
            })

        # Sort by total amount
        categories.sort(key=lambda x: x["total_amount"], reverse=True)

        return {
            "categories": categories,
            "total_categories": len(categories),
            "highest_spending_category": categories[0] if categories else None,
            "lowest_spending_category": categories[-1] if categories else None
        }

    def get_trend_analysis(self, months: int = 6) -> Dict[str, Any]:
        """Get spending trend analysis"""
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)

        bills = self.db.query(Bill).filter(
            and_(
                Bill.due_date >= start_date,
                Bill.due_date <= end_date
            )
        ).order_by(Bill.due_date).all()

        # Group by month
        monthly_data = {}
        for bill in bills:
            month_key = f"{bill.due_date.year}-{bill.due_date.month:02d}"
            if month_key not in monthly_data:
                monthly_data[month_key] = {"amount": 0, "count": 0}
            monthly_data[month_key]["amount"] += float(bill.amount)
            monthly_data[month_key]["count"] += 1

        # Calculate trend
        amounts = [data["amount"] for data in monthly_data.values()]
        if len(amounts) >= 2:
            trend = "increasing" if amounts[-1] > amounts[0] else "decreasing"
            change_percent = ((amounts[-1] - amounts[0]) / amounts[0]) * 100 if amounts[0] > 0 else 0
        else:
            trend = "stable"
            change_percent = 0

        return {
            "months_analyzed": months,
            "monthly_data": monthly_data,
            "trend": trend,
            "change_percent": round(change_percent, 2),
            "average_monthly": sum(amounts) / len(amounts) if amounts else 0
        }

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        current_month = self.get_monthly_summary()

        # Last month comparison
        last_month = date.today().replace(day=1) - timedelta(days=1)
        last_month_summary = self.get_monthly_summary(last_month.year, last_month.month)

        # Category analysis
        category_analysis = self.get_category_analysis()

        # Upcoming and overdue counts
        upcoming_count = self.db.query(Bill).filter(
            and_(
                Bill.due_date >= date.today(),
                Bill.due_date <= date.today() + timedelta(days=30),
                Bill.status == BillStatus.PENDING
            )
        ).count()

        overdue_count = self.db.query(Bill).filter(
            and_(
                Bill.due_date < date.today(),
                Bill.status == BillStatus.PENDING
            )
        ).count()

        return {
            "current_month_total": current_month["total_amount"],
            "last_month_total": last_month_summary["total_amount"],
            "average_monthly": (current_month["total_amount"] + last_month_summary["total_amount"]) / 2,
            "month_over_month_change": current_month["total_amount"] - last_month_summary["total_amount"],
            "top_category": category_analysis["highest_spending_category"]["name"] if category_analysis["highest_spending_category"] else "N/A",
            "total_categories": category_analysis["total_categories"],
            "upcoming_bills_count": upcoming_count,
            "overdue_bills_count": overdue_count,
            "current_month_bills": current_month["total_bills"],
            "payment_completion_rate": (current_month["paid_bills"] / current_month["total_bills"]) * 100 if current_month["total_bills"] > 0 else 0
        }
