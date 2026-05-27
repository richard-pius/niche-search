provider "aws" {
  region = var.region
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = { Name = "niche-search-vpc" }
}

# Public subnets
resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.region}a"
  map_public_ip_on_launch = true
  tags = { Name = "public-a" }
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.region}b"
  map_public_ip_on_launch = true
  tags = { Name = "public-b" }
}

# Private subnets for app
resource "aws_subnet" "private_app_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = "${var.region}a"
  tags = { Name = "private-app-a" }
}

resource "aws_subnet" "private_app_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.11.0/24"
  availability_zone = "${var.region}b"
  tags = { Name = "private-app-b" }
}

# Private subnets for database
resource "aws_subnet" "private_db_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.20.0/24"
  availability_zone = "${var.region}a"
  tags = { Name = "private-db-a" }
}

resource "aws_subnet" "private_db_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.21.0/24"
  availability_zone = "${var.region}b"
  tags = { Name = "private-db-b" }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
}

# NAT instance security group
resource "aws_security_group" "nat" {
  name        = "nat-sg"
  vpc_id      = aws_vpc.main.id
  
  # Allow internal VPC traffic for NAT routing
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }

  # Allow SSH access from the internet so PuTTY can connect
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Amazon Linux 2 AMI for NAT
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# NAT EC2 Instance
resource "aws_instance" "nat" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = "t3.micro" 
  subnet_id              = aws_subnet.public_a.id
  vpc_security_group_ids = [aws_security_group.nat.id]
  source_dest_check      = false
  key_name               = var.key_name
  tags = { Name = "nat-instance" }
  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
    sysctl -p
    iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
  EOF
}

# Public route table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_b" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public.id
}

# Private route table 
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block           = "0.0.0.0/0"
    network_interface_id = aws_instance.nat.primary_network_interface_id
  }
}

resource "aws_route_table_association" "private_app_a" {
  subnet_id      = aws_subnet.private_app_a.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_app_b" {
  subnet_id      = aws_subnet.private_app_b.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_db_a" {
  subnet_id      = aws_subnet.private_db_a.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_db_b" {
  subnet_id      = aws_subnet.private_db_b.id
  route_table_id = aws_route_table.private.id
}

# Security Groups
resource "aws_security_group" "alb" {
  name        = "alb-sg"
  vpc_id      = aws_vpc.main.id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "web" {
  name        = "web-sg"
  vpc_id      = aws_vpc.main.id
  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [aws_subnet.public_a.cidr_block]   # only from bastion
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "db" {
  name        = "db-sg"
  vpc_id      = aws_vpc.main.id
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }
}

# Application Load Balancer
resource "aws_lb" "app" {
  name               = "niche-search-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.public_a.id, aws_subnet.public_b.id]
}

resource "aws_lb_target_group" "app" {
  name     = "niche-search-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  health_check {
    path = "/"
    port = "80"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# Ubuntu AMI for the app server
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# App EC2 Instance
resource "aws_instance" "app" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro" 
  subnet_id              = aws_subnet.private_app_a.id
  vpc_security_group_ids = [aws_security_group.web.id]
  iam_instance_profile   = aws_iam_instance_profile.app_profile.name
  key_name               = var.key_name
  tags = { Name = "django-app-server" }
  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io nginx
    systemctl enable docker
  EOF
}

resource "aws_lb_target_group_attachment" "app" {
  target_group_arn = aws_lb_target_group.app.arn
  target_id        = aws_instance.app.id
  port             = 80
}

# RDS PostgreSQL
resource "aws_db_subnet_group" "db" {
  name       = "niche-db-subnet"
  subnet_ids = [aws_subnet.private_db_a.id, aws_subnet.private_db_b.id]
}

# Database Instance 
resource "aws_db_instance" "app" {
  identifier           = "niche-search-db"
  engine               = "postgres"
  engine_version       = "15" 
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  db_name              = "niche_search"
  username             = "db_admin"
  password             = var.db_password
  db_subnet_group_name = aws_db_subnet_group.db.name
  vpc_security_group_ids = [aws_security_group.db.id]
  skip_final_snapshot  = true
  publicly_accessible  = false
}

# S3 bucket for media
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "media" {
  bucket        = "niche-search-media-${random_id.bucket_suffix.hex}"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "media" {
  bucket                  = aws_s3_bucket.media.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM role for EC2
resource "aws_iam_role" "app_role" {
  name = "niche-app-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_policy" "s3_media" {
  name = "S3MediaAccess"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"]
      Resource = "${aws_s3_bucket.media.arn}/*"
    }]
  })
}

resource "aws_iam_policy" "cloudwatch_logs" {
  name = "CloudWatchLogsAccess"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
      Resource = "*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "attach_s3" {
  role       = aws_iam_role.app_role.name
  policy_arn = aws_iam_policy.s3_media.arn
}

resource "aws_iam_role_policy_attachment" "attach_logs" {
  role       = aws_iam_role.app_role.name
  policy_arn = aws_iam_policy.cloudwatch_logs.arn
}

resource "aws_iam_instance_profile" "app_profile" {
  name = "niche-app-instance-profile"
  role = aws_iam_role.app_role.name
}

# CloudWatch CPU alarm
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "niche-search-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Alarm when EC2 CPU exceeds 80%"
  dimensions = {
    InstanceId = aws_instance.app.id
  }
}