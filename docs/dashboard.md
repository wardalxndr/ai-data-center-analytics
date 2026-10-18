# Dashboard - AI Data Center Analytics (Looker Studio)

Live report: [AI Data Center Analytics](https://datastudio.google.com/reporting/6192c6dc-90c3-45ae-990a-458f665d5557)

Data source: BigQuery dataset `epoch_ai_dataset`. The marts are dbt **views**,
so Looker reads live data; refreshing = re-run flow 08 + `dbt run`.

## Tiles and design

| Tile | Requirement | Backing mart | Design note |
|---|---|---|---|
| Total Power by Country | 1, bar / categorical | `mart_country_power` | Reads the 93-row dimension only; scans ~1.3 KB per refresh |
| Avg Days from Groundbreaking to Full Power | 2, line / temporal | `mart_build_velocity` | Computes per-site start and peak dates from `timelines`; scans ~19.5 KB per refresh |
| APAC Focus table + memo | 3, deliverable | `mart_owner_power` / `mart_country_power` | The Johor vs Batam decision view (Malaysia 895 MW, Indonesia 72 MW) |
| Map | 4, bonus | `data_centers` | Site locations for the delivery story |

## Verified numbers (re-verified Oct 18, 2026)

Checked against BigQuery directly:

- `data_centers`: 93 rows; `timelines`: 548 rows (both match the flow ASSERTs).
- `dbt run`: PASS 5 of 5; `dbt test`: PASS 14 of 14.
- Measured scan cost per full dashboard load: 1,315 + 19,543 bytes (~21 KB),
  effect = $0.0000001 at $6.25/TiB on-demand. Effectively free, and measured,
  not assumed.

## Refreshing the dashboard

1. Run Kestra flow `08_gcp_epoch` (uploads raw to GCS, loads curated NDJSON,
   ASSERTs 93 / 548).
2. `dbt run` then `dbt test` in `epoch_analytics/` (expect 5/5 and 14/14).
3. Looker is live: no extract schedule, no manual refresh.

## Snapshot note

All figures describe the Oct 2026 Epoch AI snapshot. Upstream updates trip
the ASSERTs first; see ADR 0006 for the rebase procedure.
