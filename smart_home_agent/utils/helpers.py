"""
Utility helper functions
"""
import re
from datetime import datetime, date
from typing import Any, Optional, Dict
from decimal import Decimal, InvalidOperation


def parse_amount(amount_str: str) -> Optional[float]:
    """Parse amount string to float"""
    if not amount_str:
        return None

    # Remove currency symbols and spaces
    cleaned = re.sub(r'[\$,\s]', '', str(amount_str))

    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def parse_date(date_str: str) -> Optional[date]:
    """Parse date string to date object"""
    if not date_str:
        return None

    # Common date formats
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%m-%d-%Y",
        "%d-%m-%Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return None


def format_currency(amount: float, currency: str = "$") -> str:
    """Format amount as currency"""
    try:
        return f"{currency}{amount:,.2f}"
    except (ValueError, TypeError):
        return f"{currency}0.00"


def sanitize_string(text: str, max_length: int = None) -> str:
    """Sanitize string input"""
    if not text:
        return ""

    # Strip whitespace and normalize
    sanitized = str(text).strip()

    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip()

    return sanitized


def extract_category_from_text(text: str) -> Optional[str]:
    """Extract category from text using patterns"""
    text_lower = text.lower()

    # Category mapping
    category_patterns = {
        "utilities": ["electric", "electricity", "gas", "water", "sewer", "utilities"],
        "subscriptions": ["netflix", "spotify", "subscription", "streaming", "amazon prime"],
        "maintenance": ["maintenance", "repair", "hvac", "plumbing", "electrician"],
        "insurance": ["insurance", "policy", "coverage"],
        "rent": ["rent", "mortgage", "housing"],
        "internet": ["internet", "cable", "wifi", "broadband"],
        "transportation": ["car", "auto", "gas", "fuel", "parking", "uber", "lyft"]
    }

    for category, patterns in category_patterns.items():
        if any(pattern in text_lower for pattern in patterns):
            return category.title()

    return None


def validate_email(email: str) -> bool:
    """Validate email address"""
    if not email:
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number"""
    if not phone:
        return False

    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)

    # Check if it's a valid US phone number (10 or 11 digits)
    return len(digits) in [10, 11]


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text with suffix"""
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def safe_float_conversion(value: Any) -> float:
    """Safely convert value to float"""
    if value is None:
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, str):
        try:
            return float(value.replace(',', ''))
        except ValueError:
            return 0.0

    return 0.0


def generate_bill_summary(bills: list) -> Dict[str, Any]:
    """Generate summary statistics for a list of bills"""
    if not bills:
        return {
            "total_amount": 0.0,
            "count": 0,
            "average_amount": 0.0,
            "categories": {}
        }

    total_amount = sum(safe_float_conversion(bill.get("amount", 0)) for bill in bills)
    count = len(bills)
    average_amount = total_amount / count if count > 0 else 0.0

    # Category breakdown
    categories = {}
    for bill in bills:
        category = bill.get("category", {}).get("name", "Unknown")
        if category not in categories:
            categories[category] = {"count": 0, "amount": 0.0}
        categories[category]["count"] += 1
        categories[category]["amount"] += safe_float_conversion(bill.get("amount", 0))

    return {
        "total_amount": total_amount,
        "count": count,
        "average_amount": average_amount,
        "categories": categories
    }
