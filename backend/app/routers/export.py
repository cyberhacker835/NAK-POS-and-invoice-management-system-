import csv
import io
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Product, Customer, Invoice, InvoiceItem


router = APIRouter()


def to_csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    with io.StringIO() as s:
        writer = csv.DictWriter(s, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
        return s.getvalue()


@router.get("/products.csv")
def export_products(business_id: int, db: Session = Depends(get_db)):
    items = db.query(Product).filter(Product.business_id == business_id).all()
    rows = [
        {
            "id": p.id,
            "business_id": p.business_id,
            "name": p.name,
            "sku": p.sku or "",
            "price_aed": float(p.price_aed),
            "stock_qty": p.stock_qty,
        }
        for p in items
    ]
    csv_str = to_csv(rows)
    return Response(csv_str, media_type="text/csv")


@router.get("/customers.csv")
def export_customers(business_id: int, db: Session = Depends(get_db)):
    items = db.query(Customer).filter(Customer.business_id == business_id).all()
    rows = [
        {
            "id": c.id,
            "business_id": c.business_id,
            "name": c.name,
            "contact": c.contact or "",
            "trn": c.trn or "",
        }
        for c in items
    ]
    csv_str = to_csv(rows)
    return Response(csv_str, media_type="text/csv")


@router.get("/invoices.csv")
def export_invoices(business_id: int, db: Session = Depends(get_db)):
    items = db.query(Invoice).filter(Invoice.business_id == business_id).all()
    rows = [
        {
            "id": i.id,
            "number": i.number,
            "date": i.date.isoformat(),
            "due_date": i.due_date.isoformat() if i.due_date else "",
            "subtotal_aed": float(i.subtotal_aed),
            "vat_aed": float(i.vat_aed),
            "total_aed": float(i.total_aed),
            "status": i.status,
        }
        for i in items
    ]
    csv_str = to_csv(rows)
    return Response(csv_str, media_type="text/csv")

