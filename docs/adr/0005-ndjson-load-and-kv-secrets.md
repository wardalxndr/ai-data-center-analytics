# ADR 0005: NDJSON load + Kestra KV for credentials (OSS has no Secrets)

**Status:** Accepted (Oct 2026)

## Context

Two friction points shaped this pipeline:

1. The source CSV text contains stray quotes and embedded newlines (site
   descriptions). A naive CSV load breaks or silently mangles rows.
2. Kestra OSS does not include namespace Secrets (Enterprise-only), but the
   flows still need a project id and a service account JSON.

## Decision

- Load **newline-delimited JSON (NDJSON)** to BigQuery instead of CSV. One
  JSON object per line is immune to quotes and embedded newlines in any
  field.
- Store `GCP_PROJECT_ID` and `GCP_SERVICE_ACCOUNT` (full JSON) in the Kestra
  KV store, read with `kv()` at runtime. Never committed, never in the flow
  files. Bucket and dataset come in as flow inputs with defaults that match
  the Terraform outputs.
- The GCS loader service account gets object-create permission only: no
  read, no list. Verified: listing the bucket with this key returns 403,
  by design.

## Consequences

- Good: the load is robust to messy text without bespoke escaping.
- Good: credentials live in the orchestrator's store, not in git; rotation
  is one KV edit.
- Cost: NDJSON is larger on the wire than CSV. Irrelevant at KB scale.
- Cost: KV values are visible to anyone who can use the namespace. Fine for
  a single-user local Kestra; production would use a secret manager and a
  dedicated service account per environment.
- Known limit: a 403 `storage.objects.list` on the raw bucket is expected
  behavior, not a bug. It is documented in the README troubleshooting
  section so future-me does not "fix" it.

## Alternatives considered

- CSV load with custom escaping: fragile, and the failure mode is silent
  row corruption.
- Base64 blobs in BigQuery: harder to inspect with SQL.
- Config committed to the repo: never.
