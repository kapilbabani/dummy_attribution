terraform {
  required_providers {
    null = {
      source = "hashicorp/null"
      version = ">= 3.0.0"
    }
  }
  required_version = ">= 1.0.0"
}

provider "null" {}

resource "null_resource" "example" {
  provisioner "local-exec" {
    command = "echo 'Terraform setup complete.'"
  }
} 