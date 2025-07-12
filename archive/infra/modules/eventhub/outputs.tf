# modules/eventhub/outputs.tf
output "connection_string" {
  value     = azurerm_eventhub_namespace.main.default_primary_connection_string
  sensitive = true
}

output "topic_name" {
  value = azurerm_eventhub.main.name
}