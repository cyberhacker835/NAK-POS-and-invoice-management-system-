from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Customer
from ..schemas import CustomerCreate, CustomerOut


router = APIRouter()


@router.post("/", response_model=CustomerOut)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/", response_model=list[CustomerOut])
def list_customers(business_id: int, q: str | None = Query(None), db: Session = Depends(get_db)):
    query = db.query(Customer).filter(Customer.business_id == business_id)
    if q:
        query = query.filter(Customer.name.ilike(f"%{q}%"))
    return query.order_by(Customer.id.desc()).all()


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: int, payload: CustomerCreate, db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for k, v in payload.model_dump().items():
        setattr(customer, k, v)
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()
    return {"ok": True}

