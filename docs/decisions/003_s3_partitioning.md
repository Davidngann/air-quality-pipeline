# ADR 003 - S3 Partition Strategy

**Date:** 2026-05-22  
**Status:** Accepted

## Context

Raw air quality data from OpenAQ lands in S3 before being processed by Glue. The partition scheme determines how downstream tools e.g., Glue, Athena, and Redshift filter and data efficiently


## Decision

Use Hive-style partitioning on time dimensions:

Historical:
raw/historical/year=YYYY/month=MM/location_{id}_{YYYY}_{MM}.json

Incremental:
raw/incremental/year=YYYY/month=MM/day=DD/location_{id}_{YYYY}_{MM}_{DD}.json

### Rationale

**Hive-Style over plain date paths**: Glue Crawlers auto-infer year/month/day as partition columsn from key=value syntax without manual declaration.

**Time as partition key over station or pollutant**: Every business question in the data will likely be filter by date. Station and pollutant are high-cardinality dimensions better handled by columnar filtering inside parquet file than the partition pruning.

**Monthly granularity for historical, day granularity for incremental**: Historical backfill at day granularity would require ~65,000 API calls (ex: 30 stations × 2,190 days from 2020). Monthly granularity reduces this 
to ~2,160 calls (30 stations × 72 months) by fetching a full month per call at 1,000 results per page which is within rate limits. Incremental data is pulled daily since only the previous day's readings are needed.


## Consequences

- Changing the partition scheme after data is loaded requires
re-uploading all objects with new keys.
- Lifecycle policy applies to historical only, not incremental:  
Standard-IA has a minimum billable object size of 128KB. Incremental daily files will likely be below this threshold.  
Applying Standard-IA to incremental files would incur higher costs then keeping them in Standard storage.  
Small incremental files will be consolidated into monthly parquet during Glue ETL, addressing the small files problem downstream.