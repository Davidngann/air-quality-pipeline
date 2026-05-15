# ADR 002 - IAM Setup and Least Privilege Policy

**Date:** 2026-05-15  
**Status:** Accepted

## Context

AWS requires an identity and access management strategy before any services are provisioned. The root account must not be used for daily work. Service roles need scoped permissions.

## Decision

### Account Structure
- Root account: MFA enabled. Used only for billing and account-level settings. Never used for CLI or daily work.
- IAM user `david-de`: AdministratorAccess for personal development work. 
  AWS CLI configured with named profile `david-de`.

### Service Role: `aq-glue-role`
Created a dedicated IAM role for AWS Glue with least-privilege S3 access:
| Permission | Bucket | Reason |
|---|---|---|
| `s3:GetObject`, `s3:ListBucket` | `aq-raw-david-*` | Glue reads raw data |
| `s3:PutObject`, `s3:DeleteObject` | `aq-staged-david-*` | Glue writes staged output |

Glue is explicitly denied write access to the raw bucket — raw data 
is an immutable archive.

Trust policy allows only `glue.amazonaws.com` to assume this role.


## Consequences

- Every new AWS service (Redshift, EC2) requires its own dedicated role. 
  No shared roles across services.
- IAM policies will be migrated to Terraform in week 11.
- Policy JSON stored in `terraform/` directory for future IaC structure.