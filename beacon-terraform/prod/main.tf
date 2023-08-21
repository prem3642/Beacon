provider "aws" {
  region = "us-east-1"
}

# Configure the Cloudflare provider
provider "cloudflare" {
}

# VPC
# =========================================================

# Create a VPC to launch our instances into
resource "aws_vpc" "default" {
  cidr_block = "10.0.0.0/16"
}

# Create an internet gateway to give our subnet access to the outside world
resource "aws_internet_gateway" "default" {
  vpc_id = "${aws_vpc.default.id}"
}

# Grant the VPC internet access on its main route table
resource "aws_route" "internet_access" {
  route_table_id         = "${aws_vpc.default.main_route_table_id}"
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = "${aws_internet_gateway.default.id}"
}

# Create a subnet to launch our instances into
resource "aws_subnet" "default" {
  vpc_id                  = "${aws_vpc.default.id}"
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
}

# Elastic IP Resource
# =========================================================
resource "aws_eip" "prod" {
  vpc      = true
}

resource "aws_eip_association" "eip_assoc" {
  instance_id   = "${aws_instance.web.id}"
  allocation_id = "${aws_eip.prod.id}"
}

# Cloudflare Resource
# =========================================================
# Create a record for prod instance IP
resource "cloudflare_record" "beacon-prod" {
  domain = "fueled.engineering"
  name   = "backend.beacon-prod"
  value  = "${aws_eip.prod.public_ip}"
  type   = "A"
  # ttl    = 3600
}

# EC2 Resource
# =========================================================
resource "aws_key_pair" "auth" {
  key_name   = "${var.key_name}"
  public_key = "${file(var.public_key_path)}"
}

# Our default security group to access
# the instances over SSH and HTTP
resource "aws_security_group" "default" {
  name        = "beacon-sg-prod"
  description = "Prod security group for beacon"
  # vpc_id      = "${aws_vpc.default.id}"

  # SSH access from anywhere
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP access from the anywhere
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP access from the anywhere
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # outbound internet access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


resource "aws_instance" "web" {
  # The connection block tells our provisioner how to
  # communicate with the resource (instance)
  connection {
    # The default username for our AMI
    user = "ubuntu"

    # The connection will use the local SSH agent for authentication.
  }

  instance_type = "t2.micro"

  root_block_device = {
    volume_type = "gp2"
    volume_size = "20"
  }

  ebs_block_device = {
    device_name = "/dev/sdf"
    volume_type = "gp2"
    volume_size = "30"
    # delete_on_termination = false # <<<< !!!IMPORTANT!!!
  }

  # Lookup the correct AMI based on the region
  # we specified
  ami = "${lookup(var.aws_amis, var.aws_region)}"

  # The name of our SSH keypair we created above.
  key_name = "${aws_key_pair.auth.id}"

  # Our Security group to allow HTTP and SSH access
  security_groups = ["${aws_security_group.default.name}"]

  # We're going to launch into the same subnet as our ELB. In a production
  # environment it's more common to have a separate private subnet for
  # backend instances.
  # subnet_id = "${aws_subnet.default.id}"

  monitoring = true

  tags {
    Name = "beacon prod"
  }
}

# S3 Resource
# =========================================================
resource "aws_s3_bucket" "beacon-s3" {
   bucket = "beacon-bucket"
   acl    = "public-read"

   cors_rule {
    allowed_methods = ["GET"]
    allowed_origins = ["*"]
  }

   tags {
    Name        = "beacon"
    Environment = "prod"
   }
}
# RDS Resource
# =========================================================
# Create a subnet to launch our db instances into
resource "aws_subnet" "subnet_db_1" {
  vpc_id            = "${aws_vpc.default.id}"
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1a"

  tags {
    Name = "internal_db_subnet1"
  }
}

resource "aws_subnet" "subnet_db_2" {
  vpc_id            = "${aws_vpc.default.id}"
  cidr_block        = "10.0.3.0/24"
  availability_zone = "us-east-1b"

  tags {
    Name = "internal_db_subnet2"
  }
}

resource "aws_db_subnet_group" "rds_subnet_group" {
  name = "rds_subnet_group"
  description = "DB Subnet Group"
  subnet_ids = ["${aws_subnet.subnet_db_1.id}", "${aws_subnet.subnet_db_2.id}"]
}

# Our private db security group to allow access to only default group
resource "aws_security_group" "sg_rds" {
  name = "my-db-sg"
  description = "DB Security Group"
  vpc_id = "${aws_vpc.default.id}"
  ingress {
    from_port = 5432
    to_port = 5432
    protocol = "tcp"
    security_groups = ["${aws_security_group.default.id}"]
  }
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags {
    Name = "sg_rds"
  }
}

# RDS DB Parameter Group
resource "aws_db_parameter_group" "rds_pg" {
  name = "rds-pg"
  family = "postgres9.6"
  description = "RDS parameter group"
}

# RDS
resource "aws_db_instance" "rds_postgres" {
  identifier = "rds-postgres"
  allocated_storage = 15
  engine = "postgres"
  engine_version = "9.6.3"
  instance_class = "db.t2.micro"
  parameter_group_name = "${aws_db_parameter_group.rds_pg.name}"
  # general purpose SSD
  storage_type = "gp2"
  username = "${var.db_username}"
  password = "${var.db_password}"
  backup_retention_period = 0
  vpc_security_group_ids = ["${aws_security_group.sg_rds.id}"]
  db_subnet_group_name = "${aws_db_subnet_group.rds_subnet_group.name}"
}
# Elasticache Resource
# =========================================================
