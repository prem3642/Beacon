variable "public_key_path" {
  description = <<DESCRIPTION
Path to the SSH public key to be used for authentication.
Ensure this keypair is added to your local SSH agent so provisioners can
connect.
Example: ~/.ssh/id_rsa.pub
DESCRIPTION
}

variable "key_name" {
  description = "Desired name of AWS key pair"
  default = "beacon-fueled-keys"
}

variable "aws_region" {
  description = "AWS region to launch servers."
  default     = "us-east-1"
}

# Ubuntu 16 LTS (x64)
variable "aws_amis" {
  default = {
    ap-south-1 = "ami-099fe766"
    us-east-1 = "ami-759bc50a"
    eu-central-1 = "ami-bc4925d3"
  }
}

# RDS
variable "db_username" {
  description = "Desired username for RDS"
  default = "beacon_prod"
}

variable "db_password" {
  description = "Desired password for RDS"
  default = "Fue1234!"
}
