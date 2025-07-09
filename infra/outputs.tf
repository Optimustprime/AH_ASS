# infrastructure/outputs.tf
output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "sql_server_fqdn" {
  value = azurerm_mssql_server.main.fully_qualified_domain_name
}

output "container_app_env_id" {
  value = azurerm_container_app_environment.main.id
}

output "container_app_env_default_domain" {
  value = azurerm_container_app_environment.main.default_domain
}

output "container_registry_login_server" {
  value = azurerm_container_registry.main.login_server
}

output "container_registry_admin_username" {
  value     = azurerm_container_registry.main.admin_username
  sensitive = true
}

output "container_registry_admin_password" {
  value     = azurerm_container_registry.main.admin_password
  sensitive = true
}