from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.database import get_db
from app.models.order import Order, OrderStatus
from app.models.payment import Payment
from app.models.user import User, UserRole
from app.schemas.user import UserRead

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def get_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    total_orders = db.query(func.count(Order.id)).scalar()
    active_orders = (
        db.query(func.count(Order.id))
        .filter(Order.status.notin_([OrderStatus.COMPLETED, OrderStatus.CANCELLED]))
        .scalar()
    )
    total_revenue = db.query(func.sum(Payment.amount)).scalar() or 0.0
    total_customers = (
        db.query(func.count(User.id))
        .filter(User.role == UserRole.CUSTOMER)
        .scalar()
    )
    return {
        "total_orders": total_orders,
        "active_orders": active_orders,
        "total_revenue_usd": round(total_revenue, 2),
        "total_customers": total_customers,
    }


@router.get("/users", response_model=list[UserRead])
def list_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role: UserRole,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)
