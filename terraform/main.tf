provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source   = "./modules/vpc"
  env_name = var.env_name
}

module "eks" {
  source     = "./modules/eks"
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  env_name   = var.env_name
}

module "db" {
  source     = "./modules/db"
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.database_subnets
  env_name   = var.env_name
}
