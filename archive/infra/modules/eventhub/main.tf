# modules/eventhub/main.tf
resource "azurerm_eventhub_namespace" "main" {
  name                = "ahass-${var.environment}-eventhub"
  resource_group_name = var.resource_group_name
  location           = var.location
  sku               = "Standard"
}

resource "azurerm_eventhub" "main" {
  name                = "ahass-events"
  namespace_name      = azurerm_eventhub_namespace.main.name
  resource_group_name = var.resource_group_name
  partition_count    = 2
  message_retention  = 1
}