# ADR 0001: Kestra (self-hosted, YAML in repo) over Airflow or Mage

**Status:** Accepted (Oct 2026)

## Context

The pipeline must run daily, retry failed downloads, and keep the whole
pipeline definition reviewable in git. The course default (Mage) works, but
flow definitions are code files rather than declarative YAML, which makes
diffs noisier. Airflow is the industry standard but heavy to run for two
flows.

## Decision

Use self-hosted Kestra with flows as YAML committed to the repo:

- `flows/04_postgres_epoch.yaml`: local path into Postgres (zero cloud cost,
  good for iterating on cleaning logic).
- `flows/08_gcp_epoch.yaml`: GCP path (GCS raw zone, BigQuery curated,
  ASSERTs), scheduled daily 09:00 UTC with download retries.
- Configuration via KV store (`kv()`), see ADR 0005.

## Consequences

- Good: pipeline is code. Every change is a YAML diff in a PR, reviewable
  without running anything.
- Good: one tool covers both the local and the cloud path.
- Cost: self-hosted orchestrator is an ops burden (a real deployment would
  need a server, auth, backups).
- Cost: Kestra OSS lacks namespace Secrets (Enterprise feature); mitigated
  with KV, see ADR 0005.
- Known limit: two flows share logic by convention, not by a shared library.
  At four steps that is cheaper than building a plugin.

## Alternatives considered

- Airflow: what the sibling QRIS lakehouse project uses; correct at larger
  scale, unnecessary weight for two flows.
- Mage: course default, but Python flow files diff worse than YAML for
  review purposes.
- cron + scripts: no retries, no run history, no backfill story.
