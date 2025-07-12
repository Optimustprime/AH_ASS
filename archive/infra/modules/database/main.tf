resource "azurerm_mssql_server" "main" {
  name                         = var.sql_server_name
  resource_group_name         = var.resource_group_name
  location                    = var.location
  version                     = "12.0"
  administrator_login         = var.db_username
  administrator_login_password = var.db_password
}

resource "azurerm_mssql_database" "main" {
  name           = var.sql_database_name
  server_id      = azurerm_mssql_server.main.id
  collation      = "SQL_Latin1_General_CP1_CI_AS"
  license_type   = "LicenseIncluded"
  sku_name       = var.sql_database_sku
}

resource "azurerm_mssql_firewall_rule" "allow_azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}