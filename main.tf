# Define AWS provider
provider "aws" {
  region = "us-east-2"  # Replace with your desired region
}

# Create VPC
resource "aws_vpc" "vpc1" {
  cidr_block = "10.0.0.0/16"
}

# Create internet gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc1.id
}

# Create public subnet
resource "aws_subnet" "public_subnet_1" {
  vpc_id            = aws_vpc.vpc1.id
  cidr_block        = "10.0.1.0/24"  # Adjust CIDR block as needed
  map_public_ip_on_launch = true

  tags = {
    Name = "Public Subnet 1"
  }
}

# Create EC2 instance in public subnet
resource "aws_instance" "web_instance" {
  ami           = "ami-0c55b159cbfafe1f0"  # Replace with your desired AMI ID
  instance_type = "t2.micro"               # Replace with your desired instance type
  subnet_id     = aws_subnet.public_subnet_1.id
  key_name      = "your_key_name"          # Replace with your SSH key name

  tags = {
    Name = "web_instance"
  }

  provisioner "file" {
    content     = "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>Hello, World!</title>\n</head>\n<body>\n    <h1>Hello, World!</h1>\n</body>\n</html>"
    destination = "/home/ec2-user/index.html"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo yum update -y",
      "sudo yum install -y nginx",
      "sudo systemctl start nginx",
      "sudo systemctl enable nginx",
      "sudo mv /home/ec2-user/index.html /usr/share/nginx/html/index.html",
      "sudo systemctl restart nginx"
    ]

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = file("path/to/your/private/key.pem")  # Replace with the path to your private key file
      host        = self.public_ip
    }
  }

  # Configure security group to allow inbound HTTP traffic
  security_groups = ["${aws_security_group.allow_http_access.name}"]
}

# Create security group to allow inbound HTTP traffic
resource "aws_security_group" "allow_http_access" {
  vpc_id = aws_vpc.vpc1.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Allow traffic from any IP address
  }

  tags = {
    Name = "Allow HTTP Access"
  }
}
