# Air Quality Pipeline — AWS

A data pipeline ingesting air quality measurements from OpenAQ into AWS (S3 → Glue → Redshift), orchestrated with Apache Airflow and transformed with dbt.

## Planned Stack
- **Storage:** AWS S3
- **ETL:** AWS Glue
- **Warehouse:** Redshift Serverless
- **Orchestration:** Apache Airflow (EC2)
- **Transformation:** dbt
- **IaC:** Terraform
- **CI/CD:** GitHub Actions

## Status
Phase 2 — Week 02 (Writing Bulk loader and utils)

## Architecture Decisions
See `docs/decisions/` for ADRs.
