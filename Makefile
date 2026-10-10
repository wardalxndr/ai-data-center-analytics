.PHONY: help validate infra dbt-run dbt-test

help:
	@echo "Targets:"
	@echo "  validate  terraform fmt + validate and Kestra YAML syntax"
	@echo "  infra     terraform init + apply (bucket + dataset)"
	@echo "  dbt-run   build the 5 models"
	@echo "  dbt-test  run the 14 data contracts"

validate:
	terraform fmt -check -recursive
	terraform init -backend=false
	terraform validate
	python3 -c "import yaml,glob; [yaml.safe_load(open(f)) for f in sorted(glob.glob('flows/*.yaml'))]"

infra:
	terraform init
	terraform apply

dbt-run:
	cd epoch_analytics && dbt run

dbt-test:
	cd epoch_analytics && dbt test
