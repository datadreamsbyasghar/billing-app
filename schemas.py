from typing import List, Optional
from pydantic import BaseModel, Field

class RegisterInput(BaseModel):
    username: str
    password: str
    role: Optional[str] = "staff"

class LoginInput(BaseModel):
    username: str
    password: str

class ProductInput(BaseModel):
    name: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    is_active: Optional[bool] = True

class ProductUpdatePriceInput(BaseModel):
    product_id: int
    new_price: float = Field(gt=0)

class ProductUpdateStockInput(BaseModel):
    product_id: int
    new_stock: int = Field(ge=0)

class ProductDeactivateResponse(BaseModel):
    product_id: int
    is_active: bool
    message: str

class BillItemInput(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)

class BillCreateInput(BaseModel):
    client_name: str
    phone: Optional[str] = None
    items: List[BillItemInput]
    discount: float = Field(default=0, ge=0)

class BillSummary(BaseModel):
    bill_id: int
    client_name: str
    date: str
    total_amount: float
    discount: float
    final_amount: float

class BillDetailItem(BaseModel):
    product_id: int
    name: str
    quantity: int
    price: float
    subtotal: float

class BillDetailResponse(BaseModel):
    bill_id: int
    client_id: int
    client_name: str
    date: str
    total_amount: float
    discount: float
    final_amount: float
    items: List[BillDetailItem]

class SalesSummaryResponse(BaseModel):
    start_date: str
    end_date: str
    total_bills: int
    total_revenue: float
    total_discount: float
    final_revenue: float
    items_sold: int

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str   # ✅ add this