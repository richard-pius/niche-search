variable "db_password" {
  type      = string
  sensitive = true
}

variable "key_name" {
  type        = string
  description = "EC2 key pair name"
  default     = "niche-search-key"   # change to your actual key pair name
}

variable "region" {
  default = "us-east-1"
}