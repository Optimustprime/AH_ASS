# modules/databricks/main.tf
resource "azurerm_databricks_workspace" "main" {
  name                = "ahass-${var.environment}-databricks"
  resource_group_name = var.resource_group_name
  location           = var.location
  sku               = "standard"
}