# Redshift Serverless

## REFERENCE

### Connection Details
- **Host:** stored in `.env` as `REDSHIFT_HOST`
- **Port:** 5439
- **Database:** `dev`
- **Schemas:** `staging`, `reporting`
- **Schema details:** see `docs/data_dictionary.md`

### Staging Tables
staging.measurements
- Grain: one row per sensor per measurement timestamp  
- DISTKEY: station_id  
- SORTKEY: measurement_utc  
- Populated by: Glue job (Week 16)  

staging.stations  
- Grain: one row per monitoring station  
- DISTSTYLE: ALL (small dimension table, replicated to all slices)  
- Populated by: Glue job (Week 16)  

## Routine Operations

**Check workgroup status**  
Run command `make rs-status`

**Verify staging tables exist**  
Run command `make rs-verify-table`

**Ending a session**  
No action required. Redshift Serverless does not charge for idle time.


## Troubleshooting

### Common Failures

**Connection timeout in DBeaver**
- Check security group inbound rule: port 5439 from our IP
- Our IP may have changed  update the inbound rule
- Check the public accessibility configuration on the redshift workgroup

**Query returns 0 rows in staging tables**
- Expected until Week 16 — Glue job populates staging
- Verify tables exist: make rs-test

**psycopg2 OperationalError**
- Check .env has correct REDSHIFT_HOST, REDSHIFT_USER, REDSHIFT_PASSWORD
- Verify workgroup is AVAILABLE: make rs-status