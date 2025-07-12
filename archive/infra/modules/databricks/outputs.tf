# modules/databricks/outputs.tf
output "workspace_url" {
  value = azurerm_databricks_workspace.main.workspace_url
}