terraform {
  backend "s3" {
    bucket = "hypatys-tf"
    key    = "terraform.tfstate"
    region = "us-east-2"
    encrypt = true
  }
}

provider "aws" {
  region = "us-east-2"
}
