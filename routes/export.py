from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from io import StringIO
import csv
from fastapi.responses import StreamingResponse

from models import Bill, Client, BillItem, Product
from database import get_db   # ✅ DB session comes from database.py
from security import get_current_user, ensure_admin  # ✅ auth helpers live in security.py

router = APIRouter()

@router.get("/export/monthly_csv")
def export_monthly_csv(year: int, month: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    ensure_admin(user)
    start_dt = datetime(year, month, 1)
    end_dt = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

    bills = db.query(Bill, Client).join(Client, Bill.client_id == Client.client_id).filter(Bill.date >= start_dt, Bill.date < end_dt).order_by(Bill.date.asc()).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["bill_id", "date", "client_name", "total_amount", "discount", "final_amount"])
    for b, c in bills:
        writer.writerow([b.bill_id, b.date.isoformat(), c.name, b.total_amount, b.discount, b.final_amount])

    writer.writerow([])
    writer.writerow(["bill_id", "product_id", "product_name", "quantity", "price", "subtotal"])
    for b, _ in bills:
        items = db.query(BillItem, Product).join(Product, BillItem.product_id == Product.product_id).filter(BillItem.bill_id == b.bill_id).all()
        for bi, p in items:
            writer.writerow([b.bill_id, p.product_id, p.name, bi.quantity, bi.price, bi.subtotal])

    output.seek(0)
    filename = f"sales_{year}_{month:02d}.csv"
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="{filename}"'})