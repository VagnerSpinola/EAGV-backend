variable "project_name" {
  description = "Application name used in Azure resources."
  type        = string
  default     = "eagv-backend"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region for the resources."
  type        = string
  default     = "Brazil South"
}

variable "resource_group_name" {
  description = "Resource group name for backend resources."
  type        = string
}

variable "app_service_sku_name" {
  description = "Azure App Service plan SKU."
  type        = string
  default     = "F1"
}

variable "python_version" {
  description = "Python runtime version for the FastAPI web app."
  type        = string
  default     = "3.11"
}

variable "azure_storage_container_name" {
  description = "Public blob container used to store system settings images."
  type        = string
  default     = "system-settings-assets"
}

variable "postgresql_sku_name" {
  description = "SKU name for PostgreSQL Flexible Server."
  type        = string
  default     = "B_Standard_B1ms"
}

variable "postgresql_storage_mb" {
  description = "Storage size in MB for PostgreSQL Flexible Server."
  type        = number
  default     = 32768
}

variable "postgresql_version" {
  description = "PostgreSQL major version."
  type        = string
  default     = "16"
}

variable "postgresql_database_name" {
  description = "Application database name."
  type        = string
  default     = "eagv"
}

variable "postgresql_admin_username" {
  description = "Admin username for PostgreSQL."
  type        = string
  default     = "eagvadmin"
}

variable "postgresql_admin_password" {
  description = "Optional admin password override for PostgreSQL."
  type        = string
  default     = null
  sensitive   = true
}

variable "postgresql_client_ip" {
  description = "Optional public client IP allowed to connect directly to PostgreSQL, useful for DBeaver."
  type        = string
  default     = null
}

variable "allowed_cors_origins" {
  description = "Comma-separated frontend origins consumed by the backend."
  type        = list(string)
  default     = ["http://localhost:5173", "http://127.0.0.1:5173"]
}

variable "bootstrap_admin_email" {
  description = "Initial admin email created automatically for the test deployment."
  type        = string
  default     = "admin@eagv.com"
}

variable "bootstrap_admin_password" {
  description = "Optional initial admin password override for the test deployment."
  type        = string
  default     = null
  sensitive   = true
}

variable "bootstrap_admin_full_name" {
  description = "Initial admin display name created automatically for the test deployment."
  type        = string
  default     = "Administrador EAGV"
}

variable "jwt_secret_key" {
  description = "JWT signing key for the API."
  type        = string
  sensitive   = true
}

variable "access_token_expire_minutes" {
  description = "Access token expiration time."
  type        = number
  default     = 60
}

variable "reset_token_expire_minutes" {
  description = "Password reset token expiration time."
  type        = number
  default     = 30
}

variable "tags" {
  description = "Common Azure resource tags."
  type        = map(string)
  default = {
    system = "EAGV"
    stack  = "backend"
  }
}