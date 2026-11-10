from .runtime import run_cli
from .service import Invoice, validate_invoice


def example():
    return {
        "invoice_number": "DEMO-001",
        "vendor": "Example Supplier",
        "gstin": "27AAPFU0939F1ZV",
        "invoice_date": "2026-01-10",
        "items": [
            {"description": "Office supplies", "quantity": "2", "unit_price": "100.00"}
        ],
        "subtotal": "200.00",
        "tax": "36.00",
        "total": "236.00",
        "confidence": 0.94,
    }


def demo():
    invoice = Invoice.model_validate(example())
    return {
        "mode": "authored_fixture_validation",
        "invoice": invoice.model_dump(mode="json"),
        "issues": validate_invoice(invoice),
        "live_extraction": False,
    }


def main():
    run_cli("billtrail", demo, ("GROQ_API_KEY",))
