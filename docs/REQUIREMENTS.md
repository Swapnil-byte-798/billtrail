# BillTrail: requirements and acceptance

## Product goal

Invoice extraction with a review trail before anything reaches the ledger. A reviewer should be able to install the package, run its tests, inspect its SQL boundaries and exercise the core workflow without a custom frontend.

## Functional requirements

- PDF text extraction and Tesseract OCR for scanned pages and images
- Decimal arithmetic, typed invoice fields, GSTIN format and date checks
- Content deduplication, leased jobs, bounded retries and a dead-letter state
- Separate reviewer credentials, corrections, an audit trail and idempotent outbox dispatch

## Acceptance conditions

1. An invoice cannot be exported before reviewer approval.
2. Repeated document bytes must resolve to the original intake.
3. Duplicate approved vendor/invoice pairs must not create two liabilities.
4. Outbox replay cannot duplicate a ledger entry.

## Quality requirements

Persist domain state transactionally; validate untrusted inputs; keep provider failures visible; avoid credential and prompt disclosure in diagnostic errors; provide an installable Python package, authenticated API, container and repeatable automated checks. Keep fixture evidence distinct from public-data and live-provider evidence.

## Scope boundary

GSTIN checks validate format, not tax registration or checksum authenticity. Model confidence is uncalibrated. Dispatch writes a local accounting ledger, not a real ERP. No accuracy claim is made without a labelled invoice corpus.

## Evaluation plan

Real PDF parsing of an authored document, arithmetic failures, concurrent intake, retry exhaustion, stale leases, reviewer correction and outbox replay. External checks need the credentials, model files or network access described in the runbook. Before publishing quality claims, create a labelled evaluation set and report sample size, metric definition, model version and measured failures. Evaluate field-level precision on consented, labelled invoices; add a real accounting connector with reconciliation before claiming ERP integration.
