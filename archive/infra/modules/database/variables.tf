
variable "sql_server_name" {
  type        = string
  description = "Name of the SQL Server"
}

variable "sql_database_name" {
  type        = string
  description = "Name of the SQL Database"
}

variable "sql_database_sku" {
  type        = string
  description = "SKU name for the SQL Database"
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