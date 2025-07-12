# modules/database/outputs.tf
output "sql_server_fqdn" {
  value = azurerm_mssql_server.main.fully_qualified_domain_name
}

output "database_name" {
  value = azurerm_mssql_database.main.name
}

output "server_id" {
  value = azurerm_mssql_server.main.id
}