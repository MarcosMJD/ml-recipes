terraform {
  required_version = ">= 1.0"
  backend "s3" {
    bucket  = "tf-state-mlops-zoomcamp"
    key     = "mlops-zoomcamp-stg.tfstate"
    region  = "eu-west-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
  # profile = no need to use (default profile is used)
}

# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity
# https://www.terraform.io/language/data-sources
data "aws_caller_identity" "current_identity" {}

# account_id is needed for the creation of the ECR
locals {
  account_id = data.aws_caller_identity.current_identity.account_id
}

# input (feature) events
module "source_kinesis_stream" {
    source              = "./modules/kinesis"
    stream_name         = "${var.source_stream_name}-${var.project_id}"
    retention_period    = 48
    shard_count         = 2
    tags                = var.project_id
}

# output (prediction) events
module "source_kinesis_stream" {
    source              = "./modules/kinesis"
    stream_name         = "${var.output_stream_name}-${var.project_id}"
    retention_period    = 48
    shard_count         = 2
    tags                = var.project_id
}

# s3 bucket for model storage
module "s3_bucket" {
  source = "./modules/s3"
  bucket_name = "${var.bucket_name}-${var.project_id}"
}

# ecr image
module "ecr_image" {
   source = "./modules/ecr"
   ecr_repo_name = "${var.ecr_repo_name}_${var.project_id}"
   account_id = local.account_id
   lambda_function_local_path = var.lambda_function_local_path
   docker_image_local_path = var.docker_image_local_path
}

# Lambda module needs output stream arn, that is created in kinesis module

# lambda
module "lambda_function" {
  source = "./modules/lambda"
  image_uri = module.ecr_image.image_uri
  lambda_function_name = "${var.lambda_function_name}_${var.project_id}"
  model_bucket = module.s3_bucket.name
  output_stream_name = "${var.output_stream_name}-${var.project_id}"
  output_stream_arn = module.output_kinesis_stream.stream_arn
  source_stream_name = "${var.source_stream_name}-${var.project_id}"
  source_stream_arn = module.source_kinesis_stream.stream_arn
}


