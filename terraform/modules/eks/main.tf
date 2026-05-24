resource "aws_security_group" "eks" {
  name        = "${var.env_name}-eks-sg"
  description = "EKS Security Group"
  vpc_id      = var.vpc_id
}
