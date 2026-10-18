# Architecture Decision Records (ADR)

Short documents that record **why** this pipeline is built this way, not just what it does.
Each ADR states the context, the decision, the honest downsides, and the alternatives that were rejected.

| # | Decision | Status |
|---|---|---|
| [0001](0001-kestra-over-airflow.md) | Kestra (self-hosted, YAML-in-repo) over Airflow or Mage | Accepted |
| [0002](0002-terraform-minimal-scope.md) | Terraform owns exactly the bucket + dataset; dbt owns tables | Accepted |
| [0003](0003-row-count-asserts-drift-gate.md) | Row count ASSERTs inside the flow as the source-drift gate | Accepted |
| [0004](0004-unpartitioned-dimension-partitioned-series.md) | Unpartitioned 93-row dimension, partitioned time series | Accepted |
| [0005](0005-ndjson-load-and-kv-secrets.md) | NDJSON load + Kestra KV for credentials (OSS has no Secrets) | Accepted |
| [0006](0006-pinned-snapshot-and-rebasing.md) | Pin the Oct 2026 snapshot; ASSERTs trip first, rebase deliberately | Accepted |

Format is intentionally lightweight (context / decision / consequences / alternatives),
inspired by the ADR practice used in production teams.
