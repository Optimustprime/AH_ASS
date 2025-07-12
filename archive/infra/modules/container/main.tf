# modules/container/main.tf
resource "azurerm_container_registry" "main" {
  name                = "ahass${var.environment}acr"
  resource_group_name = var.resource_group_name
  location           = var.location
  sku               = var.container_registry_sku
  admin_enabled     = true
}

resource "azurerm_container_app_environment" "main" {
  name                = var.container_app_env_name
  resource_group_name = var.resource_group_name
  location           = var.location
}

resource "azurerm_container_app" "main" {
  name                         = "ahass-app"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name         = var.resource_group_name
  revision_mode              = "Single"

  template {
    container {
      name   = "main"
      image  = "${azurerm_container_registry.main.login_server}/ahass-app:latest"
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "DB_HOST"
        value = var.db_host
      }
      env {
        name  = "DB_NAME"
        value = var.db_name
      }
      env {
        name  = "DB_USER"
        value = var.db_username
      }
      env {
        name  = "DB_PASSWORD"
        value = var.db_password
      }
      env {
        name  = "KAFKA_CONNECTION_STRING"
        value = var.kafka_connection_string
      }
      env {
        name  = "KAFKA_TOPIC"
        value = var.kafka_topic
      }
    }
  }
}