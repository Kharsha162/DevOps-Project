resource "aws_security_group" "db" {
  name   = "${var.env_name}-db-sg"
  vpc_id = var.vpc_id
}
