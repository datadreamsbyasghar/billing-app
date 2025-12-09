from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse

from models import Bill, Client, BillItem, Product
from database import get_db   # ✅ DB session comes from database.py
from security import get_current_user, ensure_staff_or_admin  # ✅ auth helpers live in security.py

router = APIRouter()

@router.get("/bills/{bill_id}/invoice")
def render_invoice_html(bill_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    ensure_staff_or_admin(user)
    bill = db.query(Bill).filter(Bill.bill_id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    client = db.query(Client).filter(Client.client_id == bill.client_id).first()
    items = db.query(BillItem, Product).join(Product, BillItem.product_id == Product.product_id).filter(BillItem.bill_id == bill_id).all()

    # Build table rows
    rows = "".join(
        f"<tr><td>{p.name}</td>"
        f"<td style='text-align:right'>{bi.quantity}</td>"
        f"<td style='text-align:right'>{bi.price:.2f}</td>"
        f"<td style='text-align:right'>{bi.subtotal:.2f}</td></tr>"
        for (bi, p) in items
    )

    # Full HTML invoice
    html = f"""
    <html>
    <head>
      <title>Invoice #{bill.bill_id}</title>
      <style>
        body {{ font-family: Arial, sans-serif; margin: 24px; }}
        h1 {{ margin-bottom: 4px; }}
        .meta {{ margin-bottom: 16px; color: #444; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border-bottom: 1px solid #ddd; padding: 8px; }}
        th {{ text-align: left; background: #f7f7f7; }}
        .totals td {{ font-weight: bold; }}
      </style>
    </head>
    <body>
      <h1>Invoice #{bill.bill_id}</h1>
      <div class="meta">
        <div><strong>Date:</strong> {bill.date.isoformat()}</div>
        <div><strong>Client:</strong> {client.name if client else ""}</div>
        <div><strong>Phone:</strong> {client.phone or ""}</div>
      </div>
      <table>
        <thead>
          <tr><th>Product</th><th style="text-align:right">Qty</th><th style="text-align:right">Price</th><th style="text-align:right">Subtotal</th></tr>
        </thead>
        <tbody>
          {rows}
          <tr class="totals"><td colspan="3" style="text-align:right">Total</td><td style="text-align:right">{bill.total_amount:.2f}</td></tr>
          <tr class="totals"><td colspan="3" style="text-align:right">Discount</td><td style="text-align:right">-{bill.discount:.2f}</td></tr>
          <tr class="totals"><td colspan="3" style="text-align:right">Final</td><td style="text-align:right">{bill.final_amount:.2f}</td></tr>
        </tbody>
      </table>
    </body>
    </html>
    """

    return HTMLResponse(content=html)