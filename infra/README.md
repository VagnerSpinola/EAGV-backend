# Terraform Azure scaffold

This folder contains the Terraform baseline for the EAGV backend on Azure.

## Planned resources

- Resource Group
- Log Analytics Workspace
- Application Insights
- Linux App Service Plan
- Linux Web App for FastAPI
- PostgreSQL Flexible Server and application database

## Notes

- This is only the infrastructure definition.
- Nothing will be created until you decide to run Terraform later.
- The backend app settings mirror the current `.env.example` contract.
- You should review the database sizing, firewall rules, and secrets strategy before the first apply.

## Suggested flow later

1. Copy `terraform.tfvars.example` to `terraform.tfvars`.
2. Fill in `jwt_secret_key` and any environment-specific values.
3. Login with `az login`.
4. Run `terraform init`.
5. Run `terraform plan`.
6. Run `terraform apply` only after the Azure subscription is ready.