# AWS skeleton for the Smart City Traffic platform: EKS (compute), RDS
# Postgres (TimescaleDB-compatible managed Postgres), and MSK (managed Kafka).
# This is a STARTER, not a turnkey apply — it sketches the production shape so
# the dev docker-compose stack maps cleanly to cloud. Run `terraform init` then
# review/plan before any apply; backend + real networking are intentionally
# left for the operator.

terraform {
  required_version = ">= 1.7"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
  }
  # backend "s3" { ... }   # configure remote state per environment
}

provider "aws" {
  region = var.region
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.8"

  name = "${var.project}-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.region}a", "${var.region}b", "${var.region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
  tags               = local.tags
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "${var.project}-eks"
  cluster_version = "1.30"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets

  eks_managed_node_groups = {
    default = {
      instance_types = ["m6i.large"]
      min_size       = 2
      max_size       = 6
      desired_size   = 3
    }
  }
  tags = local.tags
}

resource "aws_db_instance" "postgres" {
  identifier            = "${var.project}-pg"
  engine                = "postgres"
  engine_version        = "16"
  instance_class        = "db.m6g.large"
  allocated_storage     = 100
  max_allocated_storage = 500
  db_name               = "traffic"
  username              = "traffic"
  password              = var.db_password # supply via TF_VAR / secrets manager
  multi_az              = true
  storage_encrypted     = true
  skip_final_snapshot   = false
  tags                  = local.tags
}

resource "aws_msk_cluster" "kafka" {
  cluster_name           = "${var.project}-kafka"
  kafka_version          = "3.8.x"
  number_of_broker_nodes = 3

  broker_node_group_info {
    instance_type   = "kafka.m5.large"
    client_subnets  = module.vpc.private_subnets
    storage_info {
      ebs_storage_info { volume_size = 100 }
    }
  }
  encryption_info {
    encryption_in_transit { client_broker = "TLS" }
  }
  tags = local.tags
}

locals {
  tags = {
    Project   = var.project
    ManagedBy = "terraform"
  }
}
