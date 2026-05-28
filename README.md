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

## Current Infrastructure
### Infrastructure
- AWS account: IAM user david-de, MFA on root
- S3: aq-raw-david-853407830340 (4 months Melbourne data, Jan-Apr 2026)
- Redshift Serverless: aq-melbourne-wg (ap-southeast-2)
  - staging.measurements (DISTKEY station_id, SORTKEY measurement_utc)
  - staging.stations (DISTSTYLE ALL)

## Status
Phase 2 — Week 03 (Connect to Redshift via DBeaver and Python)

## Architecture Decisions
See `docs/decisions/` for ADRs.
