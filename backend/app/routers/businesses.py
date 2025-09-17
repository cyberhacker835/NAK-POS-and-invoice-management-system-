from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Business
from ..schemas import BusinessCreate, BusinessOut


router = APIRouter()


@router.post("/", response_model=BusinessOut)
def create_business(payload: BusinessCreate, db: Session = Depends(get_db)):
    business = Business(**payload.model_dump())
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


@router.get("/", response_model=list[BusinessOut])
def list_businesses(db: Session = Depends(get_db)):
    return db.query(Business).order_by(Business.id.desc()).all()


@router.get("/{business_id}", response_model=BusinessOut)
def get_business(business_id: int, db: Session = Depends(get_db)):
    business = db.get(Business, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business


@router.put("/{business_id}", response_model=BusinessOut)
def update_business(business_id: int, payload: BusinessCreate, db: Session = Depends(get_db)):
    business = db.get(Business, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    for k, v in payload.model_dump().items():
        setattr(business, k, v)
    db.commit()
    db.refresh(business)
    return business


@router.delete("/{business_id}")
def delete_business(business_id: int, db: Session = Depends(get_db)):
    business = db.get(Business, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    db.delete(business)
    db.commit()
    return {"ok": True}

