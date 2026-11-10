# BillTrail

Invoice extraction with a review trail before anything reaches the ledger.

[![Python verification](https://github.com/Swapnil-byte-798/billtrail/actions/workflows/ci.yml/badge.svg)](https://github.com/Swapnil-byte-798/billtrail/actions/workflows/ci.yml)

Project 5 in a Python and SQL AI engineering portfolio. The interface is a Python CLI and FastAPI's generated API documentation.

## What works

- PDF text extraction and Tesseract OCR for scanned pages and images
- Decimal arithmetic, typed invoice fields, GSTIN format and date checks
- Content deduplication, leased jobs, bounded retries and a dead-letter state
- Separate reviewer credentials, corrections, an audit trail and idempotent outbox dispatch

## Run it

Python 3.11 or 3.12 and Tesseract OCR. The Docker image includes Tesseract. Input is limited to 20 MB and ten PDF pages.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q
python -m billtrail demo
python -m billtrail setup
python -m billtrail serve --port 8020
```

Open http://127.0.0.1:8020/docs. `setup` prompts for credentials without displaying them, generates independent operator/reviewer tokens, and stores them in an ignored file with owner-only permissions. Use the operator token as `Authorization: Bearer ...`; account, client and tenant endpoints issue their own scoped tokens. Do not commit any of these values.

The demo is explicitly labelled: authored fixtures exercise the workflow, not a live provider. `check-keys` reports configuration only and never claims a provider has been validated.

## Credentials

GROQ_API_KEY for structured extraction. API_TOKEN and REVIEWER_TOKEN are generated separately by setup.

To reuse a provider key across these repositories, run `python -m billtrail setup --shared` before the local `setup` command. The shared prompt adds missing keys and preserves existing nonempty keys. Local environment variables take precedence. See [.env.example](.env.example) for names only; real keys are never shipped.

## Design and boundaries

PDF/image/text → OCR when needed → typed extraction → arithmetic checks → reviewer decision → transactional outbox → local ledger

GSTIN checks validate format, not tax registration or checksum authenticity. Model confidence is uncalibrated. Dispatch writes a local accounting ledger, not a real ERP. No accuracy claim is made without a labelled invoice corpus.

## Verification

Real PDF parsing of an authored document, arithmetic failures, concurrent intake, retry exhaustion, stale leases, reviewer correction and outbox replay. Common tests also cover hidden setup, configuration precedence, provider response validation, API authentication and transactional rollback.

[Verification record](evidence/verification.json) separates automated checks from provider-dependent acceptance. No result represents all possible inputs, production load, or a calibrated model-quality benchmark.

## Read further

- [Requirements and acceptance](docs/REQUIREMENTS.md)
- [Architecture and decisions](docs/ARCHITECTURE.md)
- [Runbook and key setup](docs/RUNBOOK.md)
- [Study guide](docs/STUDY_GUIDE.md)

## Next engineering milestone

Evaluate field-level precision on consented, labelled invoices; add a real accounting connector with reconciliation before claiming ERP integration.
