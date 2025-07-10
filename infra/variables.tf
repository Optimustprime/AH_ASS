# infrastructure/variables.tf
variable "resource_group_name" {
  type        = string
  description = "Name of the resource group"
  default     = "ahass-assignment-rg"
}

variable "location" {
  type        = string
  description = "Azure region location"
  default     = "centralus"
}

variable "sql_server_name" {
  type        = string
  description = "Name of the SQL Server"
  default     = "ahass-sql-server"
}

variable "sql_database_name" {
  type        = string
  description = "Name of the SQL Database"
  default     = "ahass-database"
}

variable "sql_database_sku" {
  type        = string
  description = "SKU name for the SQL Database"
  default     = "Basic"
}

variable "container_registry_sku" {
  type        = string
  description = "SKU for Container Registry"
  default     = "Basic"
}

variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"
  default     = "dev"
}

variable "db_username" {
  type        = string
  description = "Database administrator username"
  sensitive   = true
}

variable "db_password" {
  type        = string
  description = "Database administrator password"
  sensitive   = true
}

variable "container_app_env_name" {
  type        = string
  description = "Name of the Container App Environment"
  default     = "ahass-container-env"
}
variable "image_tag" {
  type        = string
  description = "Container image tag to deploy"
  default     = "latest"
}

variable "event_hub_connection_string" {
  type        = string
  description = "Connection string for the Azure Event Hub"
  sensitive   = true
}

