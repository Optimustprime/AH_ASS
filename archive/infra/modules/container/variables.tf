# modules/container/variables.tf

variable "container_registry_sku" {
  type = string
}

variable "container_app_env_name" {
  type = string
}

variable "db_host" {
  type = string
}

variable "db_name" {
  type = string
}

variable "kafka_connection_string" {
  type      = string
  sensitive = true
}

variable "kafka_topic" {
  type = string
}