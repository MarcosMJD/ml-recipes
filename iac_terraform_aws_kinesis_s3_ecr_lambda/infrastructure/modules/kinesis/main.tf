resource "aws_kinesis_stream" "stream" {
  name             = var.stream_name
  shard_count      = var.shard_count
  retention_period = var.retention_period
  shard_level_metrics = var.shard_level_metrics
  tags = {
    CreatedBy = var.tags
  }
}

# This can be placed in a separate output.tf file
# https://www.terraform.io/language/values/outputs
output "stream_arn" {
  value = aws_kinesis_stream.stream.arn
}