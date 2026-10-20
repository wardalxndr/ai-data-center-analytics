# ADR 0006: Pin the Oct 2026 snapshot; ASSERTs trip first, rebase deliberately

**Status:** Accepted (Oct 2026)

## Context

Epoch AI updates their dataset continuously. This project's README, memo and
dashboard all quote specific numbers (93 sites, 548 timeline rows, Malaysia
895 MW, Indonesia 72 MW, build speed 900 vs 3000 days). If the upstream data
moves, those numbers become quietly wrong, which is worse than obviously
wrong.

## Decision

Treat the whole project as a **pinned snapshot**, dated in the README
("Accessed Oct 2026"):

1. The row count ASSERTs (ADR 0003) trip on the first upstream change, so
   the pipeline stops before the dashboard misleads.
2. Rebasing is an explicit, manual sequence: re-download, inspect the new
   shape, fix the column mapping, update ASSERT counts, re-run flows +
   dbt, then update every quoted number in the README and memo.

## Consequences

- Good: every figure in the docs is dated and verifiable against a known
  snapshot.
- Good: no silent staleness. The failure is loud and the fix path is written
  down.
- Cost: the project intentionally does not auto-follow upstream. A
  "live" version would need different decisions (drift-tolerant tests,
  parameterized numbers in docs).
- Cost: dashboards go stale until the rebase happens.

## Alternatives considered

- Auto-follow upstream: every doc number becomes a moving target.
- Pin without ASSERTs: the snapshot silently diverges from upstream with no
  signal at all.
- Snapshot the CSVs into the repo: possible, but they are Epoch's CC-BY
  data and the raw zone in GCS already keeps the exact loaded bytes.

## Amendment (Oct 20, 2026): first rebase executed

Upstream moved (93 → 94 sites, 548 → 560 timeline rows, Malaysia
895 → 1,138 MW with 3 sites, US 11,851 MW / 84% of tracked power). The
written rebase sequence was executed:

- Re-downloaded the CSVs, inspected the new shape: no column-mapping
  change needed; the pipeline computes cleanly on the new files.
- ASSERTs updated in `flows/08_gcp_epoch.yaml` (94 / 560) and the PINNED
  constants in `pipeline/make_dashboard_data.py` now match.
- Every quoted number in the README, memo and dashboard was rebased,
  including the build-speed claim: 2024 starts reach full power in
  ~600 days vs ~1,800 for 2019 starts (was ~900 vs ~3,000 on the old
  snapshot).
- BigQuery re-run against the new counts is still pending (needs a GCP
  session); the local dashboard marks no drift because its raw CSVs are
  the new pin itself.
