from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base   # ✅ import Base from database.py

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="staff")  # roles: "admin" | "staff"

class Client(Base):
    __tablename__ = "clients"
    client_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    total_spent = Column(Float, default=0)
    bills = relationship("Bill", back_populates="client", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

class Bill(Base):
    __tablename__ = "bills"
    bill_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_amount = Column(Float, nullable=False)
    discount = Column(Float, default=0, nullable=False)
    final_amount = Column(Float, nullable=False)

    client = relationship("Client", back_populates="bills")
    items = relationship("BillItem", back_populates="bill", cascade="all, delete-orphan")

class BillItem(Base):
    __tablename__ = "bill_items"
    bill_item_id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.bill_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    bill = relationship("Bill", back_populates="items")