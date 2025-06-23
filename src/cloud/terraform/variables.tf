variable "ami_maatalys" {
  description = "AMI ID for the EC2 instance"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "project_name" {
  description = "Nome do projeto"
  type        = string
  default     = "maatalys"
}

variable "image_url" {
  description = "Nome base da imagem Docker"
  type        = string
  default     = "maatalys:latest"
}

variable "environment" {
  description = "Deployment environment (e.g. dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "db_instance_class" {
  description = "RDS instance size"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Initial storage (GiB)"
  type        = number
  default     = 20
}

variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "14.7"
}

variable "db_name" {
  description = "Name of the initial Postgres database"
  type        = string
  default     = "maatalys-db"
}

variable "kafka_cluster_name" {
  description = "Name of the initial Postgres database"
  type        = string
  default     = "maatalys-kafka"
}
