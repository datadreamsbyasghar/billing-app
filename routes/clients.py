from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models import Client, Bill
from database import get_db   # ✅ DB session comes from database.py
from security import get_current_user, ensure_staff_or_admin  # ✅ auth helpers live in security.py

router = APIRouter()

@router.get("/clients/list")
def list_clients(db: Session = Depends(get_db), user = Depends(get_current_user)):
    ensure_staff_or_admin(user)
    clients = db.query(Client).order_by(Client.name.asc()).all()
    return [{"client_id": c.client_id, "name": c.name, "phone": c.phone, "total_spent": c.total_spent or 0} for c in clients]

@router.get("/clients/by_name/{client_name}/history")
def client_history_by_name(client_name: str, db: Session = Depends(get_db), user = Depends(get_current_user)):
    ensure_staff_or_admin(user)
    client = db.query(Client).filter(Client.name == client_name).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    bills = db.query(Bill).filter(Bill.client_id == client.client_id).order_by(Bill.date.desc()).all()
    return {
        "client_id": client.client_id,
        "name": client.name,
        "phone": client.phone,
        "total_spent": client.total_spent or 0,
        "bills": [
            {
                "bill_id": b.bill_id,
                "date": b.date.isoformat(),
                "total_amount": b.total_amount,
                "discount": b.discount,
                "final_amount": b.final_amount,
            }
            for b in bills
        ],
    }

@router.get("/clients/{client_id}/history")
def client_history(client_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    ensure_staff_or_admin(user)
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    bills = db.query(Bill).filter(Bill.client_id == client_id).order_by(Bill.date.desc()).all()
    return {
        "client_id": client.client_id,
        "name": client.name,
        "phone": client.phone,
        "total_spent": client.total_spent or 0,
        "bills": [
            {
                "bill_id": b.bill_id,
                "date": b.date.isoformat(),
                "total_amount": b.total_amount,
                "discount": b.discount,
                "final_amount": b.final_amount,
            }
            for b in bills
        ],
    }