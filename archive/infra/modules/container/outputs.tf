# modules/container/outputs.tf
output "container_app_url" {
  value = azurerm_container_app.main.latest_revision_fqdn
}

output "registry_login_server" {
  value = azurerm_container_registry.main.login_server
}