variable "project" {
  type    = string
  default = "smart-city-traffic"
}

variable "region" {
  type    = string
  default = "eu-central-1"
}

variable "db_password" {
  type      = string
  sensitive = true
  # Supply via TF_VAR_db_password or AWS Secrets Manager — never commit it.
}
