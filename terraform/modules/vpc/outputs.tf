output "vpc_id" {
  value = aws_vpc.main.id
}
output "private_subnets" {
  value = ["10.0.1.0/24", "10.0.2.0/24"]
}
output "database_subnets" {
  value = ["10.0.10.0/24", "10.0.11.0/24"]
}
