terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "epoch-ai-data-center"
  region  = "us-central1"
}

# 1. Membuat Data Lake (Google Cloud Storage)
resource "google_storage_bucket" "epoch_data_lake" {
  # Nama bucket HARUS unik secara global di seluruh dunia. 
  # Ganti "ward" dengan angka/nama unik jika error nama sudah dipakai.
  name     = "epoch-ai-data-lake-ward"
  location = "US"
  # Demo only. true lets terraform destroy a non-empty bucket on teardown.
  # Keep false for anything you care about.
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

# 2. Membuat Data Warehouse (Google BigQuery)
resource "google_bigquery_dataset" "epoch_data_warehouse" {
  dataset_id = "epoch_ai_dataset"
  location   = "US"
}

output "bucket" {
  value = google_storage_bucket.epoch_data_lake.url
}

output "dataset" {
  value = google_bigquery_dataset.epoch_data_warehouse.dataset_id
}
