# ADR 0004: Unpartitioned 93-row dimension, partitioned time series

**Status:** Accepted (Oct 2026)

## Context

BigQuery design must follow query patterns, not visual symmetry. The two
curated tables have opposite shapes: `data_centers` is a small dimension
(one row per site), `timelines` is a time series (power over time per site).

## Decision

- `data_centers`: `CLUSTER BY country, owner`, deliberately **no
  partitioning**. A 93-row dimension gains nothing from partitions;
  partitioning would add cost and complexity with zero pruning benefit.
- `timelines`: `PARTITION BY date` plus clustering on `data_center`, because
  every mart filters or groups by date.

## Where this lives in code

Both tables are created by the BigQuery load tasks in
`flows/08_gcp_epoch.yaml`, so the optimization is set on the load jobs
themselves:

- `load_centers`: `clusteringFields: [country, owner]`, no partitioning.
- `load_timelines`: `timePartitioningField: date`, `timePartitioningType: DAY`,
  `clusteringFields: [data_center]`.

This placement matters: `WRITE_TRUNCATE` into an existing table preserves
that table's partitioning and clustering, so only the create path defines the
shape. Before this fix the live tables were optimized while the flow was not,
which meant a fresh project would come out unoptimized. That gap is closed.

Verified two ways (Oct 18, 2026):

1. Live metadata: `time_partitioning` and `clustering_fields` read back from
   both tables in `epoch_ai_dataset`.
2. Scratch replay: a throwaway dataset was loaded with the exact job config
   above (autodetect maps `YYYY-MM-DD` strings to a DATE column, which field
   partitioning requires) and produced identical metadata with identical row
   counts (93 / 548). Scratch dataset deleted afterwards.

## Consequences

- Good: date-filtered marts prune partitions on the table where it matters.
- Good: the honest note travels with the repo: at 93/548 rows neither choice
  changes the bill. The transferable part is the reasoning pattern.
- Good: the dbt marts stay views on purpose. They are 9-12 row aggregates
  over already-optimized tables; materializing and partitioning them would
  add cost without changing any query plan.
- Cost: reviewers expecting "partition everything" need the explanation. It
  lives in the README and here, with measured evidence in `docs/dashboard.md`.
- Known limit: if `timelines` grows to billions of rows, clustering columns
  should be re-chosen from the real query log, not assumed.

## Alternatives considered

- Partition both tables: symmetry without benefit on the dimension.
- Partition neither: misses the teaching goal and wastes scans if the time
  series grows.
- Materialize the marts as partitioned tables (the pattern used in the
  sibling QRIS project): rejected here because the marts are tiny aggregates;
  the partitioning that matters is on the 548-row time series they read.

## Amendment (Oct 20, 2026)

Snapshot rebased from 93/548 to 94/560 (ADR 0006 amendment). The decision
and its rationale are unchanged: the dimension is still a ~94-row table
where partitioning buys nothing, and the time series still reads better
partitioned by date. Row counts in the verification notes above stay as
they were recorded historically.
