locals {
  base_name            = lower(replace("${var.project_name}-${var.environment}", "_", "-"))
  safe_name            = substr(replace(local.base_name, "-", ""), 0, 18)
  storage_account_name = substr("st${local.safe_name}${random_string.suffix.result}", 0, 24)
  backend_cors_origins = join(",", var.allowed_cors_origins)
  postgresql_admin_password = coalesce(
    var.postgresql_admin_password,
    random_password.postgresql_admin.result,
  )
  bootstrap_admin_password = coalesce(
    var.bootstrap_admin_password,
    random_password.bootstrap_admin.result,
  )
}

resource "random_string" "suffix" {
  length  = 5
  special = false
  upper   = false
}

resource "random_password" "bootstrap_admin" {
  length           = 24
  special          = true
  override_special = "!@#%^*-_"
}

resource "random_password" "postgresql_admin" {
  length           = 24
  special          = true
  override_special = "!@#%^*-_"
}

resource "azurerm_resource_group" "this" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

resource "azurerm_service_plan" "this" {
  name                = "asp-${local.base_name}"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  os_type             = "Linux"
  sku_name            = var.app_service_sku_name
  tags                = var.tags
}

resource "azurerm_storage_account" "this" {
  name                            = local.storage_account_name
  resource_group_name             = azurerm_resource_group.this.name
  location                        = azurerm_resource_group.this.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  access_tier                     = "Hot"
  allow_nested_items_to_be_public = true
  min_tls_version                 = "TLS1_2"
  tags                            = var.tags
}

resource "azurerm_storage_container" "system_settings_assets" {
  name                  = var.azure_storage_container_name
  storage_account_name  = azurerm_storage_account.this.name
  container_access_type = "blob"
}

resource "azurerm_postgresql_flexible_server" "this" {
  name                   = "psql-${local.safe_name}-${random_string.suffix.result}"
  resource_group_name    = azurerm_resource_group.this.name
  location               = azurerm_resource_group.this.location
  version                = var.postgresql_version
  administrator_login    = var.postgresql_admin_username
  administrator_password = local.postgresql_admin_password
  zone                   = "1"
  storage_mb             = var.postgresql_storage_mb
  sku_name               = var.postgresql_sku_name
  backup_retention_days  = 7
  tags                   = var.tags
}

resource "azurerm_postgresql_flexible_server_database" "this" {
  name      = var.postgresql_database_name
  server_id = azurerm_postgresql_flexible_server.this.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_azure_services" {
  name             = "allow-azure-services"
  server_id        = azurerm_postgresql_flexible_server.this.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_client_ip" {
  count            = var.postgresql_client_ip != null ? 1 : 0
  name             = "allow-client-ip"
  server_id        = azurerm_postgresql_flexible_server.this.id
  start_ip_address = var.postgresql_client_ip
  end_ip_address   = var.postgresql_client_ip
}

resource "azurerm_linux_web_app" "this" {
  name                = "app-${local.base_name}-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  service_plan_id     = azurerm_service_plan.this.id
  https_only          = true
  tags                = var.tags

  site_config {
    always_on        = false
    app_command_line = "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

    application_stack {
      python_version = var.python_version
    }
  }

  app_settings = {
    PROJECT_NAME                    = "EAGV Backend"
    API_V1_PREFIX                   = "/api/v1"
    DATABASE_URL                    = "postgresql+psycopg://${var.postgresql_admin_username}:${urlencode(local.postgresql_admin_password)}@${azurerm_postgresql_flexible_server.this.fqdn}:5432/${azurerm_postgresql_flexible_server_database.this.name}?sslmode=require"
    DATABASE_AUTO_INITIALIZE        = "true"
    AZURE_STORAGE_CONNECTION_STRING = azurerm_storage_account.this.primary_connection_string
    AZURE_STORAGE_CONTAINER_NAME    = azurerm_storage_container.system_settings_assets.name
    JWT_SECRET_KEY                  = var.jwt_secret_key
    JWT_ALGORITHM                   = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES     = tostring(var.access_token_expire_minutes)
    RESET_TOKEN_EXPIRE_MINUTES      = tostring(var.reset_token_expire_minutes)
    BACKEND_CORS_ORIGINS            = local.backend_cors_origins
    BOOTSTRAP_ADMIN_EMAIL           = var.bootstrap_admin_email
    BOOTSTRAP_ADMIN_PASSWORD        = local.bootstrap_admin_password
    BOOTSTRAP_ADMIN_FULL_NAME       = var.bootstrap_admin_full_name
    SCM_DO_BUILD_DURING_DEPLOYMENT  = "true"
    WEBSITES_PORT                   = "8000"
  }
}