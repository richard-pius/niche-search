variable "db_password" {
  type      = string
  sensitive = true
}
variable "key_name" {
  type        = string
  description = "Your EC2 key pair name"
  default     = "niche-search-key"
}
variable "region" {
  default = "ap-south-1"
}