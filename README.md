# Epoch AI Data Center Analytics – APAC Delivery Focus

Dashboard: https://datastudio.google.com/reporting/6192c6dc-90c3-45ae-990a-458f665d5557
Author: Ward (BINUS, AWS PM Intern APAC Data Center Delivery target)

## Problem
Where is AI capacity growing, how fast to build, where next in APAC? US dominates 35GW, APAC only 4 countries tracked. Delivery must choose Johor vs Batam.

## Source (not mine)
Epoch AI – AI Data Centers (CC-BY): https://epoch.ai/data/ai-data-centers
- `data_centers.csv` (93 sites), `data_center_timelines.csv` (~545 rows)
- Accessed Oct 2026. Analysis mine.

## Architecture (batch, daily 09:00 UTC)
Kestra `04_postgres_epoch` + `08_gcp_epoch` → GCS `gs://epoch-ai-data-lake-ward/raw/` → BigQuery `epoch-ai-data-center.epoch_ai_dataset` (data_centers CLUSTER BY country,owner; timelines PARTITION BY date) → dbt (stg + mart_country_power + mart_yearly_power + mart_owner_power + mart_build_velocity) → Looker

## Dashboard (2 required + 2 bonus)
1. Total Power by Country – AI Data Centers (bar, categorical)
2. Average Days from Groundbreaking to Full Power – AI Data Centers (line, temporal)
3. APAC Focus table + memo (Malaysia 661 MW, Indonesia 72 MW)
4. Map (bonus)

## How to run
1. `terraform apply` in `01-docker-terraform` (bucket + dataset, US)
2. Kestra: set KV GCP_PROJECT_ID/BUCKET/DATASET/LOCATION, Secrets GCP_CREDS, import YAMLs, Execute
3. BigQuery: check COUNT 93 / 545
4. dbt: `dbt run` in `epoch_analytics` (expect PASS=5)
5. Open Looker link

## My decision (memo)
Malaysia leads APAC (Johor). Recommend Johor expansion + Batam next. Avg build 800 days (2024) vs 3000 (2019) – delivery faster now. Risk: grid + water.
