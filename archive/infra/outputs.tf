# infra/outputs.tf
  output "resource_group_name" {
    value = azurerm_resource_group.main.name
  }

  output "database" {
    value = {
      server_fqdn    = module.database.sql_server_fqdn
      database_name  = module.database.database_name
      server_id      = module.database.server_id
    }
    sensitive = true
  }

  output "container" {
    value = {
      app_url           = module.container.container_app_url
      registry_server   = module.container.registry_login_server
    }
  }

  output "eventhub" {
    value = {
      topic_name = module.eventhub.topic_name
    }
  }

  output "storage" {
    value = {
      account_name = module.storage.storage_account_name
    }
    sensitive = true
  }

  output "databricks" {
    value = {
      workspace_url = module.databricks.workspace_url
    }
  }