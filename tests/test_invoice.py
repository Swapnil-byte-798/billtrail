from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from pydantic import ValidationError
from billtrail.cli import example
from billtrail.runtime import Fault
from billtrail.service import Invoice, InvoiceService, read_document, validate_invoice


class FakeExtractor:
    def __init__(self, value=None, failure=False):
        self.value = value or example()
        self.failure = failure
        self.calls = 0

    def ask(self, *args):
        self.calls += 1
        if self.failure:
            raise Fault("Provider unavailable", 502)
        return deepcopy(self.value)


class InvoiceTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.extractor = FakeExtractor()
        self.now = 1000
        self.service = InvoiceService(
            Path(self.directory.name) / "test.db", self.extractor, lambda: self.now
        )

    def tearDown(self):
        self.directory.cleanup()

    def intake(self, suffix=b""):
        return self.service.ingest(
            "invoice.txt",
            b"Invoice DEMO-001 Office supplies 2 x 100 tax 36 total 236" + suffix,
        )["id"]

    def extracted(self, suffix=b""):
        identifier = self.intake(suffix)
        self.service.process(identifier)
        return identifier

    def test_balanced_decimal_invoice(self):
        self.assertEqual(validate_invoice(Invoice.model_validate(example())), [])

    def test_total_mismatch(self):
        value = example() | {"total": "250.00"}
        self.assertIn(
            "invoice_total_mismatch", validate_invoice(Invoice.model_validate(value))
        )

    def test_quantity_arithmetic(self):
        value = example()
        value["items"][0]["quantity"] = "3"
        self.assertIn(
            "line_item_subtotal_mismatch",
            validate_invoice(Invoice.model_validate(value)),
        )

    def test_invalid_gstin_and_negative_values(self):
        for field, value in [
            ("gstin", "invalid"),
            ("tax", "-1"),
            ("confidence", 2),
            ("items", []),
        ]:
            with self.subTest(field=field), self.assertRaises(ValidationError):
                Invoice.model_validate(example() | {field: value})

    def test_future_date_and_low_confidence_review(self):
        value = Invoice.model_validate(
            example() | {"invoice_date": "2099-01-01", "confidence": 0.3}
        )
        self.assertEqual(len(validate_invoice(value)), 2)

    def test_content_deduplication(self):
        first = self.intake()
        self.assertEqual(self.intake(), first)

    def test_parallel_intake_deduplicates(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            identifiers = list(pool.map(lambda _: self.intake(), range(4)))
        self.assertEqual(len(set(identifiers)), 1)

    def test_extraction_requires_human_review(self):
        identifier = self.extracted()
        self.assertEqual(self.service.get(identifier)["state"], "review")
        self.assertEqual(self.service.dispatch()["delivered"], 0)

    def test_completed_extraction_is_not_repeated(self):
        identifier = self.extracted()
        self.service.process(identifier)
        self.assertEqual(self.extractor.calls, 1)

    def test_invalid_arithmetic_cannot_be_approved(self):
        self.extractor.value["total"] = "999.00"
        identifier = self.extracted()
        with self.assertRaises(Fault):
            self.service.review(identifier, True)

    def test_human_correction_and_outbox(self):
        self.extractor.value["total"] = "999.00"
        identifier = self.extracted()
        self.service.review(identifier, True, example())
        self.assertEqual(self.service.dispatch()["delivered"], 1)
        self.assertEqual(self.service.dispatch()["delivered"], 0)

    def test_duplicate_vendor_invoice_is_rejected(self):
        first = self.extracted()
        second = self.extracted(b" duplicate scan")
        self.service.review(first, True)
        with self.assertRaises(Fault):
            self.service.review(second, True)
        self.assertEqual(self.service.get(second)["state"], "review")

    def test_three_transient_failures_go_to_dead_letter(self):
        self.extractor.failure = True
        identifier = self.intake()
        for _ in range(3):
            self.service.process(identifier)
            self.now += 10
        self.assertEqual(self.service.get(identifier)["state"], "dead_letter")

    def test_retry_backoff_is_enforced(self):
        self.extractor.failure = True
        identifier = self.intake()
        self.service.process(identifier)
        with self.assertRaises(Fault):
            self.service.process(identifier)

    def test_bad_schema_is_a_permanent_failure(self):
        self.extractor.value = {"not": "an invoice"}
        identifier = self.intake()
        self.assertEqual(self.service.process(identifier)["state"], "dead_letter")

    def test_rejected_invoice_never_reaches_accounting(self):
        identifier = self.extracted()
        self.service.review(identifier, False)
        self.assertEqual(self.service.dispatch()["delivered"], 0)

    def test_review_cannot_be_repeated(self):
        identifier = self.extracted()
        self.service.review(identifier, True)
        with self.assertRaises(Fault):
            self.service.review(identifier, True)

    def test_real_pdf_text_parser(self):
        import fitz

        document = fitz.open()
        page = document.new_page()
        page.insert_text((50, 50), "Invoice DEMO-001 Office supplies total INR 236.00")
        self.assertIn("236.00", read_document(document.tobytes(), "invoice.pdf"))
        document.close()

    def test_empty_and_unsupported_uploads(self):
        for content, filename in [(b"", "a.txt"), (b"anything", "a.exe")]:
            with self.subTest(filename=filename), self.assertRaises(Fault):
                read_document(content, filename)

    def test_unknown_document(self):
        with self.assertRaises(Fault) as error:
            self.service.get("missing")
        self.assertEqual(error.exception.status, 404)
