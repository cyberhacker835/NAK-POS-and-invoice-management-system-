from datetime import datetime


AED_SYMBOL = "AED"
VAT_RATE = 0.05


def generate_invoice_number(sequence: int) -> str:
    return f"INV-{sequence:05d}"


def calculate_totals(subtotal: float) -> tuple[float, float, float]:
    vat = round(subtotal * VAT_RATE, 2)
    total = round(subtotal + vat, 2)
    return round(subtotal, 2), vat, total


def utcnow_str() -> str:
    return datetime.utcnow().isoformat()

