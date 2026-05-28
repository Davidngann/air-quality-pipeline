# ADR 002 - IAM Setup and Least Privilege Policy

**Date:** 2026-05-15  
**Status:** Accepted
**Updated:** 2026-05-25


## Context

AWS requires an identity and access management strategy before any services are provisioned. The root account must not be used for daily work. Service roles need scoped permissions.

## Decision

### Account Structure
- Root account: MFA enabled. Used only for billing and account-level settings. Never used for CLI or daily work.
- IAM user `david-de`: AdministratorAccess for personal development work. 
  AWS CLI configured with named profile `david-de`.

### Service Role
| Role | Trust Principal | Policy | Permissions |
|---|---|---|---|
| `aq-glue-role` | `glue.amazonaws.com` | `aq-glue-s3-policy` | Read raw bucket, write staged bucket |
| `aq-redshift-role` | `redshift.amazonaws.com` | `aq-redshift-s3-policy` | Read raw bucket only |


Glue is explicitly denied write access to the raw bucket — raw data 
is an immutable archive.

Redshift only requires read access to raw bucket for COPY operations. It never writes back to S3.
Each service has its own trust policy and permissions policy. No shared roles across services.


### Admin Credentials
Redshift Serverless admin password stored in `.env` (gitignored). In production, Secrets Manager with automatic rotation would replace this pattern.


## Consequences

- Every new AWS service (Redshift, EC2) requires its own dedicated role. 
  No shared roles across services.
- IAM policies will be migrated to Terraform in week 11.
- Policy JSON stored in `terraform/` directory for future IaC structure.