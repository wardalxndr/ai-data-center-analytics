# ADR 0002: Terraform owns exactly the bucket + dataset; dbt owns tables

**Status:** Accepted (Oct 2026)

## Context

The project needs reproducible infrastructure: a GCS raw zone and a BigQuery
dataset. Two tools in the stack can create BigQuery objects (Terraform and
dbt), and overlapping ownership causes state fights.

## Decision

Terraform (`main.tf`) provisions exactly two resources:

1. GCS bucket `epoch-ai-data-lake-ward` (US) with an
   AbortIncompleteMultipartUpload lifecycle rule.
2. BigQuery dataset `epoch_ai_dataset` (US).

Everything inside the dataset is owned by dbt. IAM and the service account
are created manually and documented as the known gap rather than
half-codified.

## Consequences

- Good: a fresh project bootstraps with `terraform init && terraform apply`;
  no click-ops for storage.
- Good: single owner per object: Terraform never touches tables, dbt never
  touches the bucket.
- Cost: `force_destroy = true` is demo-only (lets teardown delete a
  non-empty bucket). It is commented as such in the file; a production
  version must flip it.
- Cost: the provider hardcodes the project id. Fine for a single-purpose
  repo; a reusable module would parameterize it.
- Known limit: IAM not reproducible from code yet (manual service account).

## Alternatives considered

- gcloud shell scripts: imperative, no state, no plan step.
- All objects in Terraform, including dbt tables: dbt then fights Terraform
  on every run.
- dbt-only (no Terraform): dbt cannot create the bucket, and a dataset
  created implicitly by the first run is invisible infrastructure.
