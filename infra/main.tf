import {
  to = azurerm_resource_group.main
  id = "/subscriptions/218034c1-34e2-4baf-8e4d-7ceadffb3900/resourceGroups/ahass-assignment-rg"
}
import {
  to = azurerm_mssql_firewall_rule.allow_azure_services
  id = "/subscriptions/218034c1-34e2-4baf-8e4d-7ceadffb3900/resourceGroups/ahass-assignment-rg/providers/Microsoft.Sql/servers/ahass-sql-server/firewallRules/AllowAzureServices"
}
import {
  to = azurerm_container_app.main
  id = "/subscriptions/218034c1-34e2-4baf-8e4d-7ceadffb3900/resourceGroups/ahass-assignment-rg/providers/Microsoft.App/containerApps/django-app"
}
provider "azurerm" {
  features {}
}




terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }

    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.0"
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

resource "azurerm_role_assignment" "sql_access" {
  scope                = azurerm_mssql_server.main.id
  role_definition_name = "Contributor" # Replace with a valid role
  principal_id         = azurerm_container_app.main.identity[0].principal_id

  depends_on = [
    azurerm_container_app.main,
    azurerm_mssql_server.main
  ]
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
  name                = lower(replace("${var.resource_group_name}acr", "-", ""))
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  sku               = var.container_registry_sku
  admin_enabled     = true

  tags = {
    environment = var.environment
  }

  identity {
    type = "SystemAssigned"
  }
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

  identity {
    type = "SystemAssigned"
  }

  registry {
    server               = azurerm_container_registry.main.login_server
    username            = azurerm_container_registry.main.admin_username
    password_secret_name = "registry-password"
  }

  secret {
    name  = "registry-password"
    value = azurerm_container_registry.main.admin_password
  }

  template {
    container {
      name   = "django-app"
      image  = "${azurerm_container_registry.main.login_server}/django-app:latest"
      cpu    = "0.5"
      memory = "1Gi"

      env {
        name  = "DB_HOST"
        value = azurerm_mssql_server.main.fully_qualified_domain_name
      }

      env {
        name  = "DB_NAME"
        value = azurerm_mssql_database.main.name
      }

      env {
        name  = "DB_USER"
        value = var.db_username
      }

      env {
        name  = "DB_PASS"
        value = var.db_password
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
    allow_insecure_connections = true
    external_enabled = true
    target_port     = 8000
    transport       = "auto"

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  depends_on = [
    azurerm_container_registry.main,
    azurerm_container_app_environment.main
  ]

}

resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_container_app.main.identity[0].principal_id

  depends_on = [
    azurerm_container_app.main,
    azurerm_container_registry.main
  ]

  lifecycle {
    ignore_changes = [
      principal_id
    ]
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

resource "azurerm_role_assignment" "event_hub_sender" {
  scope                = azurerm_eventhub_namespace.kafka.id
  role_definition_name = "Azure Event Hubs Data Sender"
  principal_id         = azurerm_container_app.main.identity[0].principal_id

  depends_on = [
    azurerm_eventhub_namespace.kafka,
    azurerm_container_app.main
  ]
}


resource "azurerm_eventhub_consumer_group" "databricks" {
  name                = "databricks-consumer"
  namespace_name      = azurerm_eventhub_namespace.kafka.name
  eventhub_name       = azurerm_eventhub.ad_clicks.name
  resource_group_name = azurerm_resource_group.main.name
}


resource "azurerm_databricks_workspace" "main" {
  name                = "${var.resource_group_name}-databricks"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "standard"

  tags = {
    Environment = var.environment
  }
}

resource "databricks_secret_scope" "ahass_scope" {
  name                     = "ahass-scope"
  initial_manage_principal = "users"
}

resource "databricks_secret" "event_hub_connection_string" {
  key          = "EVENT_HUB_CONNECTION_STRING"
  string_value = var.event_hub_connection_string
  scope        = databricks_secret_scope.ahass_scope.name
}

resource "azurerm_eventhub_authorization_rule" "listen_policy" {
  name                = "ListenPolicy"
  eventhub_name       = azurerm_eventhub.ad_clicks.name
  namespace_name      = azurerm_eventhub_namespace.kafka.name
  resource_group_name = azurerm_resource_group.main.name

  listen = true
}

resource "azurerm_databricks_access_connector" "storage_connector" {
  name                = "databricks-access-connector"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  databricks_workspace_id = azurerm_databricks_workspace.main.id
  storage_account_id      = azurerm_storage_account.tfstate.id
}
