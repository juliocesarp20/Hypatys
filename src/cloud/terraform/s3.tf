resource "aws_s3_bucket" "landing" {
  bucket = "landing-layer-prd"
  acl    = "private"
  versioning { enabled = true }
}

resource "aws_s3_bucket" "bronze" {
  bucket = "bronze-layer-prd"
  acl    = "private"
  versioning { enabled = true }
}

resource "aws_s3_bucket_notification" "landing_notify" {
  bucket = aws_s3_bucket.landing.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.landing_processor.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
