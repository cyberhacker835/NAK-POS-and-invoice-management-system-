from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Invoice, InvoiceItem
from ..schemas import InvoiceCreate, InvoiceOut, InvoiceItemOut
from ..utils import calculate_totals, generate_invoice_number


router = APIRouter()


def compute_subtotal(items: List[dict]) -> float:
    subtotal = 0.0
    for item in items:
        line_total = round(float(item["unit_price_aed"]) * int(item["quantity"]), 2)
        subtotal += line_total
    return round(subtotal, 2)


@router.post("/", response_model=InvoiceOut)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)):
    next_seq = (db.query(Invoice).count() or 0) + 1
    number = payload.number or generate_invoice_number(next_seq)
    subtotal = compute_subtotal([i.model_dump() for i in payload.items])
    subtotal_aed, vat_aed, total_aed = calculate_totals(subtotal)

    invoice = Invoice(
        business_id=payload.business_id,
        customer_id=payload.customer_id,
        number=number,
        date=payload.date or date.today(),
        due_date=payload.due_date,
        notes=payload.notes,
        subtotal_aed=subtotal_aed,
        vat_aed=vat_aed,
        total_aed=total_aed,
        status=payload.status or "unpaid",
    )
    db.add(invoice)
    db.flush()

    for item in payload.items:
        line_total = round(item.unit_price_aed * item.quantity, 2)
        db.add(
            InvoiceItem(
                invoice_id=invoice.id,
                product_id=item.product_id,
                description=item.description,
                quantity=item.quantity,
                unit_price_aed=item.unit_price_aed,
                line_total_aed=line_total,
            )
        )

    db.commit()
    db.refresh(invoice)

    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).all()
    return InvoiceOut(
        id=invoice.id,
        business_id=invoice.business_id,
        customer_id=invoice.customer_id,
        number=invoice.number,
        date=invoice.date,
        due_date=invoice.due_date,
        notes=invoice.notes,
        subtotal_aed=float(invoice.subtotal_aed),
        vat_aed=float(invoice.vat_aed),
        total_aed=float(invoice.total_aed),
        status=invoice.status,
        items=[
            InvoiceItemOut(
                id=i.id,
                product_id=i.product_id,
                description=i.description,
                quantity=i.quantity,
                unit_price_aed=float(i.unit_price_aed),
                line_total_aed=float(i.line_total_aed),
            )
            for i in items
        ],
        created_at=invoice.created_at,
    )


@router.get("/", response_model=list[InvoiceOut])
def list_invoices(
    business_id: int,
    status: str | None = Query(None),
    start: date | None = Query(None),
    end: date | None = Query(None),
    customer_id: int | None = Query(None),
    min_total: float | None = Query(None),
    max_total: float | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Invoice).filter(Invoice.business_id == business_id)
    if status:
        q = q.filter(Invoice.status == status)
    if start:
        q = q.filter(Invoice.date >= start)
    if end:
        q = q.filter(Invoice.date <= end)
    if customer_id:
        q = q.filter(Invoice.customer_id == customer_id)
    if min_total is not None:
        q = q.filter(Invoice.total_aed >= min_total)
    if max_total is not None:
        q = q.filter(Invoice.total_aed <= max_total)

    invoices = q.order_by(Invoice.id.desc()).all()
    results: list[InvoiceOut] = []
    for inv in invoices:
        items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == inv.id).all()
        results.append(
            InvoiceOut(
                id=inv.id,
                business_id=inv.business_id,
                customer_id=inv.customer_id,
                number=inv.number,
                date=inv.date,
                due_date=inv.due_date,
                notes=inv.notes,
                subtotal_aed=float(inv.subtotal_aed),
                vat_aed=float(inv.vat_aed),
                total_aed=float(inv.total_aed),
                status=inv.status,
                items=[
                    InvoiceItemOut(
                        id=i.id,
                        product_id=i.product_id,
                        description=i.description,
                        quantity=i.quantity,
                        unit_price_aed=float(i.unit_price_aed),
                        line_total_aed=float(i.line_total_aed),
                    )
                    for i in items
                ],
                created_at=inv.created_at,
            )
        )
    return results


@router.put("/{invoice_id}", response_model=InvoiceOut)
def update_invoice(invoice_id: int, payload: InvoiceCreate, db: Session = Depends(get_db)):
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice.customer_id = payload.customer_id
    invoice.date = payload.date or invoice.date
    invoice.due_date = payload.due_date
    invoice.notes = payload.notes
    invoice.status = payload.status or invoice.status

    db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).delete()

    subtotal = compute_subtotal([i.model_dump() for i in payload.items])
    subtotal_aed, vat_aed, total_aed = calculate_totals(subtotal)
    invoice.subtotal_aed = subtotal_aed
    invoice.vat_aed = vat_aed
    invoice.total_aed = total_aed

    db.flush()
    for item in payload.items:
        line_total = round(item.unit_price_aed * item.quantity, 2)
        db.add(
            InvoiceItem(
                invoice_id=invoice.id,
                product_id=item.product_id,
                description=item.description,
                quantity=item.quantity,
                unit_price_aed=item.unit_price_aed,
                line_total_aed=line_total,
            )
        )
    db.commit()
    db.refresh(invoice)

    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).all()
    return InvoiceOut(
        id=invoice.id,
        business_id=invoice.business_id,
        customer_id=invoice.customer_id,
        number=invoice.number,
        date=invoice.date,
        due_date=invoice.due_date,
        notes=invoice.notes,
        subtotal_aed=float(invoice.subtotal_aed),
        vat_aed=float(invoice.vat_aed),
        total_aed=float(invoice.total_aed),
        status=invoice.status,
        items=[
            InvoiceItemOut(
                id=i.id,
                product_id=i.product_id,
                description=i.description,
                quantity=i.quantity,
                unit_price_aed=float(i.unit_price_aed),
                line_total_aed=float(i.line_total_aed),
            )
            for i in items
        ],
        created_at=invoice.created_at,
    )


@router.delete("/{invoice_id}")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).delete()
    db.delete(invoice)
    db.commit()
    return {"ok": True}

