# ADR 001 — Why AWS

**Date:** 2026-05-15  
**Status:** Accepted

## Context

I need a cloud platform to host a production-grade data pipeline for my portfolio. The pipeline involves object storage, a managed ETL service, a cloud data warehouse, and an orchestration layer.

Three options were considered: AWS, GCP, Azure.

## Decision

Chose AWS for the following reasons:

1. **Service maturity** — S3, Glue, Redshift, and IAM are battle-tested 
   services with extensive documentation and community support.
2. **Certification path** — AWS DEA-C01 (Data Engineer Associate) is a 
   recognised credential that aligns with my 9-month roadmap.
3. **Free Tier** — sufficient for learning without significant cost during 
   early weeks.

## Consequences

- All infrastructure is AWS-specific. Migrating to other cloud provider later requires relearning equivalent services.
- Certification cost ~AUD 230 (DEA-C01 exam fee).
- Monthly AWS spend estimated AUD 30–70 across Phase 2.
