# ADR 0003: Row count ASSERTs inside the flow as the source-drift gate

**Status:** Accepted (Oct 2026)

## Context

The source is an external dataset (Epoch AI) pinned to an Oct 2026 snapshot.
Upstream changes would silently corrupt every number on the dashboard. The
source CSVs carry no ingest timestamp, so dbt `source freshness` cannot work
here: there is nothing to compare against `loaded_at`.

## Decision

After loading curated tables in flow 08, ASSERT exact row counts:

- `data_centers`: 93 rows
- `timelines`: 548 rows

A mismatch fails the run loudly, before dbt runs. Freshness lives in
orchestration (the daily schedule + this gate), not in dbt.

## Consequences

- Good: upstream drift stops the pipeline before bad data reaches the marts
  or the dashboard.
- Good: the failure is precise: the ASSERT message names which count drifted.
- Cost: exact equality means legitimate upstream growth also fails. That is
  intentional for a pinned snapshot (see ADR 0006 for the rebase procedure).
- Known limit: row counts are a coarse gate. Column-level correctness is dbt
  territory: 14 tests in `models/schema.yml` (unique + not_null contracts).

## Alternatives considered

- dbt source freshness: needs a loaded_at column that does not exist.
- Warn-only checks: drift slips through and the dashboard lies quietly.
- No checks: yesterday's numbers presented as today's.
