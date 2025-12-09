from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models import Product
from schemas import ProductInput, ProductUpdatePriceInput, ProductUpdateStockInput
from database import get_db   # ✅ DB session comes from database.py
from security import get_current_user, ensure_admin, ensure_staff_or_admin  # ✅ auth helpers live in security.py

router = APIRouter()

@router.post("/products/add")
def add_product(input: ProductInput, db: Session = Depends(get_db), user = Depends(get_current_user)):
    ensure_admin(user)
    existing = db.query(Product).filter(Product.name == input.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product already exists")
    product = Product(name=input.name, price=input.price, stock=input.stock, is_active=True)
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"message": "Product added", "product_id": product.product_id}

@router.get("/products/list")
def list_products(db: Session = Depends(get_db), user = Depends(get_current_user)):
    ensure_staff_or_admin(user)
    products = db.query(Product).filter(Product.is_active == True).order_by(Product.name.asc()).all()
    return [{"product_id": p.product_id, "name": p.name, "price": p.price, "stock": p.stock} for p in products]

@router.post("/products/update_price")
def update_product_price(input: ProductUpdatePriceInput, db: Session = Depends(get_db), user = Depends(get_current_user)):
    ensure_admin(user)
    product = db.query(Product).filter(Product.product_id == input.product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.price = input.new_price
    db.commit()
    return {"message": "Price updated", "product_id": product.product_id, "price": product.price}

@router.post("/products/update_stock")
def update_product_stock(input: ProductUpdateStockInput, db: Session = Depends(get_db), user = Depends(get_current_user)):
    ensure_admin(user)
    product = db.query(Product).filter(Product.product_id == input.product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.stock = input.new_stock
    db.commit()
    return {"message": "Stock updated", "product_id": product.product_id, "stock": product.stock}

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    ensure_admin(user)
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False
    db.commit()
    return {"message": f"Product {product_id} marked inactive"}

@router.post("/products/restore/{product_id}")
def restore_product(product_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    ensure_admin(user)
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = True
    db.commit()
    return {"message": f"Product {product_id} restored", "is_active": product.is_active}