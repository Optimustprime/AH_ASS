# modules/databricks/variables.tf
variable "event_hub_connection_string" {
  type      = string
  sensitive = true
}