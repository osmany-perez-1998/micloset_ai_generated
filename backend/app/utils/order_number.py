from datetime import datetime
from sqlalchemy.orm import Session
from app.models.order import Order


def generate_order_number(db: Session) -> str:
    """Generate MC-YYYY#### — e.g. MC-20260001."""
    year = datetime.utcnow().year
    prefix = f"MC-{year}"

    # Count existing orders this year to determine sequence
    count = (
        db.query(Order)
        .filter(Order.order_number.like(f"{prefix}%"))
        .count()
    )
    return f"{prefix}{str(count + 1).zfill(4)}"
