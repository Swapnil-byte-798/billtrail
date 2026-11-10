# BillTrail: runbook

## Install and configure

Follow README.md with Python 3.11 or 3.12. Python 3.11 or 3.12 and Tesseract OCR. The Docker image includes Tesseract. Input is limited to 20 MB and ten PDF pages.

Run `python -m billtrail setup --shared` to enter reusable provider keys through hidden prompts, then `python -m billtrail setup` to generate local operator tokens. A local nonempty key overrides the shared value. Leave optional keys empty. An existing local `.env` is deliberately not overwritten; edit it locally to rotate values. `PORTFOLIO_SECRETS_FILE` changes the shared-file location. Environment variables override both files.

GROQ_API_KEY for structured extraction. API_TOKEN and REVIEWER_TOKEN are generated separately by setup. Never send keys in chat, URLs, screenshots, issue comments, command arguments or Git. The repository's placeholders are intentionally blank.

## Operate

`python -m billtrail check-keys` only reports which keys exist. `python -m billtrail serve --port 8020` starts the loopback API. The health endpoint proves process availability, not provider availability. Use `/docs` to inspect request schemas. Operator endpoints use API_TOKEN; invoice review uses REVIEWER_TOKEN; scoped client/account/tenant endpoints use the token returned at creation.

Local state defaults to `.data/` under the current working directory. API state can be relocated with the DATA_DIR environment variable. Protect the entire directory and its backups. Restarting preserves committed data; do not delete the database to repair a failed request. Inspect the service's state or report endpoint and its domain tests first.

## Container

```bash
docker build -t billtrail:local .
docker volume create billtrail-data
docker run --rm --env-file .env -p 127.0.0.1:8020:8020 -v billtrail-data:/data billtrail:local
```

The image runs as a non-root user. If using a bind mount instead of the named volume, give that user write access. A shared credential file outside the container is not mounted automatically; supply required variables securely. QuietScribe also needs a read-only mount containing prepared model weights.

## Verify changes

Run `python -m pytest -q`, `python -m billtrail demo` and `python -m pip wheel . --no-deps -w /tmp/wheels`. CI repeats unit/API checks on Python 3.11 and 3.12 and runs an installed wheel outside the checkout. No provider credentials are needed for normal CI.

Automated scope: Real PDF parsing of an authored document, arithmetic failures, concurrent intake, retry exhaustion, stale leases, reviewer correction and outbox replay.

Live acceptance remains a separate step: configure only the required provider, use a non-sensitive sample, exercise the real API path, and record model version, call count, usage, latency and any validation error. Do not substitute a demo response when a live request fails. Provider availability, pricing and limits can change independently of the code.

## Troubleshooting

- HTTP 401: verify token scope; provider keys are not application tokens.
- HTTP 409: inspect the original request/state and use the same payload when replaying a request key.
- HTTP 429: inspect the local quota and upstream limits; do not repeat blindly.
- HTTP 502/503: check configured providers, network access or required local models; errors deliberately omit upstream response bodies and credentials.
- SQLite lock errors: keep transactions short and use a single host with persistent storage; plan a database change before multiple replicas.

GSTIN checks validate format, not tax registration or checksum authenticity. Model confidence is uncalibrated. Dispatch writes a local accounting ledger, not a real ERP. No accuracy claim is made without a labelled invoice corpus.
