# BillTrail: study guide

## Explain the problem

Invoice extraction with a review trail before anything reaches the ledger. Explain who uses the workflow and why each confirmation, isolation or validation boundary exists before describing libraries.

## Read the implementation

1. Read `service.py` and its SQL schema. Name the durable entities and draw their valid state transitions.
2. Trace one successful API request from its Pydantic input to its committed writes.
3. Trace a provider failure and identify what can and cannot be rolled back.
4. Read the tests that enforce the acceptance conditions below. Explain why each failure would matter to a user.

1. An invoice cannot be exported before reviewer approval.
2. Repeated document bytes must resolve to the original intake.
3. Duplicate approved vendor/invoice pairs must not create two liabilities.
4. Outbox replay cannot duplicate a ledger entry.

## Interview discussion

- Where is the transaction boundary, and what happens if the process dies immediately after it?
- How are retries bound to the original request? Which operation can safely repeat?
- Which inputs are untrusted, and how are externally generated fields validated?
- What is tested with fixtures, what was measured on public data, and what remains unmeasured?
- What would change with ten times the data, multiple workers, or another tenant?

## Honest project explanation

Describe the implemented behavior, then demonstrate a representative test and explain its failure condition. Do not present mock latency, authored examples, uncalibrated scores or optional integrations as measured production results.

Known boundaries: GSTIN checks validate format, not tax registration or checksum authenticity. Model confidence is uncalibrated. Dispatch writes a local accounting ledger, not a real ERP. No accuracy claim is made without a labelled invoice corpus.

## Practical extension

Evaluate field-level precision on consented, labelled invoices; add a real accounting connector with reconciliation before claiming ERP integration. Define a measurable acceptance criterion before extending the implementation.
