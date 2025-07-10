# infrastructure/main.tf

provider "azurerm" {
  features {}
}

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  backend "azurerm" {
    resource_group_name  = "ahass-assignment-rg"
    storage_account_name = "ahassstorage"
    container_name      = "tfstate"
    key                 = "prod.terraform.tfstate"
  }
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_mssql_server" "main" {
  name                         = var.sql_server_name
  resource_group_name         = azurerm_resource_group.main.name
  location                    = azurerm_resource_group.main.location
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

resource "azurerm_container_registry" "main" {
  name                = "${replace(lower(var.resource_group_name), "-", "")}${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  sku                = var.container_registry_sku
  admin_enabled      = true
}

resource "azurerm_container_app_environment" "main" {
  name                = var.container_app_env_name
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
}

resource "azurerm_container_app" "main" {
  name                         = "django-app"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name         = azurerm_resource_group.main.name
  revision_mode               = "Single"

  template {
    container {
      name   = "django-app"
      image  = "${azurerm_container_registry.main.login_server}/django-app:latest"
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "DATABASE_URL"
        value = "mssql://${var.db_username}:${var.db_password}@${azurerm_mssql_server.main.fully_qualified_domain_name}:1433/${azurerm_mssql_database.main.name}"
      }

      env {
        name  = "KAFKA_CONNECTION_STRING"
        value = azurerm_eventhub_namespace.kafka.default_primary_connection_string
      }

      env {
        name  = "KAFKA_TOPIC"
        value = azurerm_eventhub.ad_clicks.name
      }

      env {
        name  = "ENV"
        value = "dev"
      }
    }
  }

  ingress {
    external_enabled = true
    target_port     = 8000
    transport       = "auto"
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}

resource "azurerm_storage_account" "tfstate" {
  name                     = "tfstate${replace(lower(var.resource_group_name), "-", "")}"
  resource_group_name      = azurerm_resource_group.main.name
  location                = azurerm_resource_group.main.location
  account_tier            = "Standard"
  account_replication_type = "LRS"

  tags = {
    environment = var.environment
  }
}

resource "azurerm_storage_container" "tfstate" {
  name                  = "tfstate"
  storage_account_name  = azurerm_storage_account.tfstate.name
  container_access_type = "private"
}

resource "azurerm_eventhub_namespace" "kafka" {
  name                = "${var.resource_group_name}-ehns"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"
  capacity            = 1
  auto_inflate_enabled = true
  maximum_throughput_units = 5
}

resource "azurerm_eventhub" "ad_clicks" {
  name                = "ad-clicks"
  namespace_name      = azurerm_eventhub_namespace.kafka.name
  resource_group_name = azurerm_resource_group.main.name
  partition_count     = 4
  message_retention   = 1
}

resource "azurerm_eventhub_consumer_group" "databricks" {
  name                = "databricks-consumer"
  namespace_name      = azurerm_eventhub_namespace.kafka.name
  eventhub_name       = azurerm_eventhub.ad_clicks.name
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_databricks_workspace" "main" {
  name                        = "${var.resource_group_name}-databricks"
  resource_group_name         = azurerm_resource_group.main.name
  location                    = azurerm_resource_group.main.location
  sku                         = "standard"

  tags = {
    Environment = var.environment
  }
}