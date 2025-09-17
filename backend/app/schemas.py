from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


AED = Field(description="Amount in AED", examples=["100.00"])  # cosmetic


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None

    class Config:
        from_attributes = True


class BusinessBase(BaseModel):
    name: str
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    contact_number1: Optional[str] = None
    contact_number2: Optional[str] = None
    trn: Optional[str] = None


class BusinessCreate(BusinessBase):
    pass


class BusinessOut(BusinessBase):
    id: int
    logo_path: Optional[str] = None
    manager_signature_path: Optional[str] = None

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    sku: Optional[str] = None
    price_aed: float
    stock_qty: int = 0


class ProductCreate(ProductBase):
    business_id: int


class ProductOut(ProductBase):
    id: int
    business_id: int

    class Config:
        from_attributes = True


class CustomerBase(BaseModel):
    name: str
    contact: Optional[str] = None
    trn: Optional[str] = None


class CustomerCreate(CustomerBase):
    business_id: int


class CustomerOut(CustomerBase):
    id: int
    business_id: int

    class Config:
        from_attributes = True


class InvoiceItemCreate(BaseModel):
    product_id: Optional[int] = None
    description: str
    quantity: int
    unit_price_aed: float


class InvoiceItemOut(InvoiceItemCreate):
    id: int
    line_total_aed: float

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    business_id: int
    customer_id: Optional[int] = None
    number: Optional[str] = None
    date: Optional[date] = None
    due_date: Optional[date] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]


class InvoiceOut(BaseModel):
    id: int
    business_id: int
    customer_id: Optional[int]
    number: str
    date: date
    due_date: Optional[date]
    notes: Optional[str]
    subtotal_aed: float
    vat_aed: float
    total_aed: float
    status: str
    items: List[InvoiceItemOut] = []
    created_at: datetime

    class Config:
        from_attributes = True

