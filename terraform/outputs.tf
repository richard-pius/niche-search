output "alb_dns" {
  value = aws_lb.app.dns_name
}
output "rds_endpoint" {
  value = aws_db_instance.app.endpoint
}
output "s3_bucket" {
  value = aws_s3_bucket.media.bucket
}
output "nat_public_ip" {
  value = aws_instance.nat.public_ip
}
output "app_private_ip" {
  value = aws_instance.app.private_ip
}