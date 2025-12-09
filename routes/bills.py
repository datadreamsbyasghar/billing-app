from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from models import Bill, BillItem, Client, Product
from schemas import BillCreateInput, BillSummary, BillDetailResponse, BillDetailItem
from database import get_db   # ✅ DB session comes from database.py
from security import get_current_user, ensure_staff_or_admin  # ✅ auth helpers live in security.py

router = APIRouter()

@router.post("/bills/create")
def create_bill(input: BillCreateInput, db: Session = Depends(get_db), user = Depends(get_current_user)):
    ensure_staff_or_admin(user)
    if not input.items:
        raise HTTPException(status_code=400, detail="Bill must contain at least one item")

    client = db.query(Client).filter(Client.name == input.client_name).first()
    if not client:
        client = Client(name=input.client_name, phone=input.phone or None)
        db.add(client)
        db.commit()
        db.refresh(client)

    total = 0.0
    prepared_items: List[BillItem] = []
    for item in input.items:
        product = db.query(Product).filter(Product.product_id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product ID {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}")

        subtotal = item.price * item.quantity
        total += subtotal
        product.stock -= item.quantity

        prepared_items.append(BillItem(product_id=item.product_id, quantity=item.quantity, price=item.price, subtotal=subtotal))

    final = total - input.discount
    if final < 0:
        raise HTTPException(status_code=400, detail="Final amount cannot be negative")

    bill = Bill(client_id=client.client_id, total_amount=total, discount=input.discount, final_amount=final)
    db.add(bill)
    db.commit()
    db.refresh(bill)

    for bi in prepared_items:
        bi.bill_id = bill.bill_id
        db.add(bi)

    client.total_spent = (client.total_spent or 0) + final
    db.commit()

    return {"message": "Bill created", "bill_id": bill.bill_id, "final_amount": final}

@router.get("/bills/list", response_model=List[BillSummary])
def list_bills(db: Session = Depends(get_db), user = Depends(get_current_user)):
    ensure_staff_or_admin(user)
    rows = db.query(Bill, Client).join(Client, Bill.client_id == Client.client_id).order_by(Bill.date.desc()).all()
    return [
        BillSummary(
            bill_id=b.bill_id,
            client_name=c.name,
            date=b.date.isoformat(),
            total_amount=b.total_amount,
            discount=b.discount,
            final_amount=b.final_amount,
        )
        for (b, c) in rows
    ]

@router.get("/bills/{bill_id}", response_model=BillDetailResponse)
def get_bill(bill_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    ensure_staff_or_admin(user)
    bill = db.query(Bill).filter(Bill.bill_id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    client = db.query(Client).filter(Client.client_id == bill.client_id).first()
    items = db.query(BillItem, Product).join(Product, BillItem.product_id == Product.product_id).filter(BillItem.bill_id == bill_id).all()

    return BillDetailResponse(
        bill_id=bill.bill_id,
        client_id=bill.client_id,
        client_name=client.name if client else "",
        date=bill.date.isoformat(),
        total_amount=bill.total_amount,
        discount=bill.discount,
        final_amount=bill.final_amount,
        items=[
            BillDetailItem(
                product_id=p.product_id,
                name=p.name,
                quantity=bi.quantity,
                price=bi.price,
                subtotal=bi.subtotal,
            )
            for (bi, p) in items
        ],
    )