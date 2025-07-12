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

  provider "azurerm" {
    features {}
  }

  resource "azurerm_resource_group" "main" {
    name     = var.resource_group_name
    location = var.location
  }

  module "database" {
    source              = "./modules/database"
    resource_group_name = azurerm_resource_group.main.name
    location           = azurerm_resource_group.main.location
    sql_server_name    = var.sql_server_name
    sql_database_name  = var.sql_database_name
    sql_database_sku   = var.sql_database_sku
    db_username        = var.db_username
    db_password        = var.db_password
  }

  module "container" {
    source                   = "./modules/container"
    resource_group_name      = azurerm_resource_group.main.name
    location                = azurerm_resource_group.main.location
    environment             = var.environment
    container_registry_sku  = var.container_registry_sku
    container_app_env_name  = var.container_app_env_name
    db_host                 = module.database.sql_server_fqdn
    db_name                 = module.database.database_name
    db_username             = var.db_username
    db_password             = var.db_password
    kafka_connection_string = module.eventhub.connection_string
    kafka_topic             = module.eventhub.topic_name
  }

  module "eventhub" {
    source              = "./modules/eventhub"
    resource_group_name = azurerm_resource_group.main.name
    location           = azurerm_resource_group.main.location
    environment        = var.environment
  }

  module "storage" {
    source              = "./modules/storage"
    resource_group_name = azurerm_resource_group.main.name
    location           = azurerm_resource_group.main.location
    environment        = var.environment
  }

  module "databricks" {
    source                     = "./modules/databricks"
    resource_group_name        = azurerm_resource_group.main.name
    location                   = azurerm_resource_group.main.location
    environment               = var.environment
    event_hub_connection_string = var.event_hub_connection_string
  }