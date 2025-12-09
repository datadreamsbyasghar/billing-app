from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from models import Bill, BillItem, Product, Client
from schemas import SalesSummaryResponse
from database import get_db   # ✅ DB session comes from database.py
from security import get_current_user, ensure_admin  # ✅ auth helpers in security.py

router = APIRouter()

@router.get("/analytics/summary", response_model=SalesSummaryResponse)
def analytics_summary(start: Optional[str] = None, end: Optional[str] = None, db: Session = Depends(get_db), user = Depends(get_current_user)):
    ensure_admin(user)
    end_dt = datetime.fromisoformat(end) if end else datetime.utcnow()
    start_dt = datetime.fromisoformat(start) if start else (end_dt - timedelta(days=30))

    totals = db.query(
        func.count(Bill.bill_id),
        func.coalesce(func.sum(Bill.total_amount), 0),
        func.coalesce(func.sum(Bill.discount), 0),
        func.coalesce(func.sum(Bill.final_amount), 0),
    ).filter(Bill.date >= start_dt, Bill.date <= end_dt).one()

    items = db.query(func.coalesce(func.sum(BillItem.quantity), 0))\
        .join(Bill, Bill.bill_id == BillItem.bill_id)\
        .filter(Bill.date >= start_dt, Bill.date <= end_dt).scalar()

    weekly_sales = db.query(
        func.date_trunc('week', Bill.date).label('week'),
        func.coalesce(func.sum(Bill.final_amount), 0).label('total')
    ).filter(Bill.date >= start_dt, Bill.date <= end_dt)\
     .group_by(func.date_trunc('week', Bill.date))\
     .order_by('week').all()

    weekly_discounts = db.query(
        func.date_trunc('week', Bill.date).label('week'),
        func.coalesce(func.sum(Bill.discount), 0).label('discount')
    ).filter(Bill.date >= start_dt, Bill.date <= end_dt)\
     .group_by(func.date_trunc('week', Bill.date))\
     .order_by('week').all()

    top_products = db.query(
        Product.name,
        func.coalesce(func.sum(BillItem.quantity), 0).label('total_sold')
    ).join(BillItem, Product.product_id == BillItem.product_id)\
     .join(Bill, Bill.bill_id == BillItem.bill_id)\
     .filter(Bill.date >= start_dt, Bill.date <= end_dt)\
     .group_by(Product.name)\
     .order_by(func.sum(BillItem.quantity).desc())\
     .limit(5).all()

    return {
        "start_date": start_dt.isoformat(),
        "end_date": end_dt.isoformat(),
        "total_bills": totals[0],
        "total_revenue": float(totals[1]),
        "total_discount": float(totals[2]),
        "final_revenue": float(totals[3]),
        "items_sold": int(items or 0),
        "weekly_sales": [{"week": str(w.week.date()), "total": float(w.total)} for w in weekly_sales],
        "weekly_discounts": [{"week": str(w.week.date()), "discount": float(w.discount)} for w in weekly_discounts],
        "top_products": [{"name": p.name, "total_sold": int(p.total_sold)} for p in top_products],
    }