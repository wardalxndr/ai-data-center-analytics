# ADR 0004: Unpartitioned 93-row dimension, partitioned time series

**Status:** Accepted (Oct 2026)

## Context

BigQuery design must follow query patterns, not visual symmetry. The two
curated tables have opposite shapes: `data_centers` is a small dimension
(one row per site), `timelines` is a time series (power over time per site).

## Decision

- `data_centers`: `CLUSTER BY country, owner`, and deliberately **no
  partitioning**. A 93-row dimension gains nothing from partitions;
  partitioning it would add cost and complexity with zero pruning benefit.
- `timelines`: `PARTITION BY date` plus clustering, because every mart
  filters or groups by date.

## Consequences

- Good: date-filtered marts prune partitions on the table where it matters.
- Good: the honest note travels with the repo: at 93/548 rows neither choice
  changes the bill. The transferable part is the reasoning pattern.
- Cost: reviewers expecting "partition everything" need the explanation.
  It lives in the README and here, with measured evidence in
  `docs/dashboard.md`.
- Known limit: if `timelines` ever grows to billions of rows, clustering
  columns should be re-chosen from the real query log, not assumed.

## Alternatives considered

- Partition both tables: symmetry without benefit on the dimension.
- Partition neither: misses the teaching goal and wastes scans if the time
  series grows.
