output "resource_group_name" {
  description = "Backend resource group name."
  value       = azurerm_resource_group.this.name
}

output "web_app_name" {
  description = "Azure Web App name."
  value       = azurerm_linux_web_app.this.name
}

output "web_app_default_hostname" {
  description = "Default backend hostname."
  value       = azurerm_linux_web_app.this.default_hostname
}

output "backend_api_base_url" {
  description = "Backend API base URL."
  value       = "https://${azurerm_linux_web_app.this.default_hostname}/api/v1"
}

output "storage_account_name" {
  description = "Azure Storage account used for public system settings assets."
  value       = azurerm_storage_account.this.name
}

output "storage_container_name" {
  description = "Blob container used for system settings assets."
  value       = azurerm_storage_container.system_settings_assets.name
}

output "storage_public_base_url" {
  description = "Public base URL for uploaded system settings assets."
  value       = "${azurerm_storage_account.this.primary_blob_endpoint}${azurerm_storage_container.system_settings_assets.name}"
}

output "postgresql_server_name" {
  description = "PostgreSQL Flexible Server name."
  value       = azurerm_postgresql_flexible_server.this.name
}

output "postgresql_fqdn" {
  description = "PostgreSQL Flexible Server hostname."
  value       = azurerm_postgresql_flexible_server.this.fqdn
}

output "postgresql_database_name" {
  description = "Application PostgreSQL database name."
  value       = azurerm_postgresql_flexible_server_database.this.name
}

output "postgresql_admin_username" {
  description = "PostgreSQL admin username."
  value       = var.postgresql_admin_username
}

output "postgresql_admin_password" {
  description = "Generated PostgreSQL admin password if one was not provided."
  value       = local.postgresql_admin_password
  sensitive   = true
}

output "bootstrap_admin_email" {
  description = "Initial admin email for the free test deployment."
  value       = var.bootstrap_admin_email
}

output "bootstrap_admin_password" {
  description = "Generated initial admin password if one was not provided."
  value       = local.bootstrap_admin_password
  sensitive   = true
}