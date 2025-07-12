# modules/storage/main.tf
resource "azurerm_storage_account" "main" {
  name                     = "ahass${var.environment}storage"
  resource_group_name      = var.resource_group_name
  location                = var.location
  account_tier           = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "data" {
  name                  = "data"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}