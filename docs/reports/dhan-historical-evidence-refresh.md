# Dhan Historical Evidence refresh

The separate refresh uses persisted Dhan Daily candles and the existing
`LargeScaleHistoricalReplayEngine` through `_run_symbol`. Daily and Weekly
point-in-time context and subsequent observations use the existing engines.
It does not append Dhan observations to the legacy provider baseline.

## Current build

- Replay window: 2021-08-18 through 2026-10-01.
- Scope: the configured current NSE 500 membership, resolved to exact NSE Dhan
  identities. This introduces survivorship bias, disclosed in report metadata.
- Input: one consistent read-only SQLite transaction, captured in
  `tmp/evidence-dhan-2026-10-01/dhan-inputs.json` and SHA-256 fingerprinted.
- Checkpoints: `replay-NNNN.json`, keyed to source hash and symbol.
- Progress: `progress.json`; final accounting: `status.json`.
- No-data, unavailable identities and ambiguous identities are explicit
  exclusions; computational failures block publication.
- Four bounded offline workers. No historical downloads, provider fallback,
  production snapshot writes, or methodology edits.

## Publication

The publisher checks every target checkpoint, source hashes, join uniqueness,
required observations/context, schema constraints and SQLite integrity.
It creates a new immutable artifact, then atomically replaces the small
`current-dhan-evidence.json` pointer. It never overwrites the baseline.

The Evidence page asks for `dataset_version=latest` metadata, pins all subsequent
queries to that exact version and shows exclusions/coverage caveats. Until an
artifact exists, it displays the labelled baseline. Existing comparable-zone
requests remain pinned to their original baseline; no ranking behavior changes.

The API code requires a safe backend deployment. Do not restart a backend
hosting an active production updater. Replay completion alone is not proof
that the refreshed report is visible in the running application.

Recent zones have shorter follow-up. The period end is an observation cutoff,
not a guarantee every security traded on that date; per-symbol first/last dates
are retained in the published metadata.
