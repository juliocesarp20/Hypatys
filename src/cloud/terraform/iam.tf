resource "aws_iam_role" "lambda_exec" {
  name = "landing-processor-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = { Service = "lambda.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  role   = aws_iam_role.lambda_exec.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["logs:CreateLogGroup","logs:CreateLogStream","logs:PutLogEvents"],
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect   = "Allow",
        Action   = ["s3:GetObject"],
        Resource = "${aws_s3_bucket.landing.arn}/*"
      },
      {
        Effect   = "Allow",
        Action   = ["s3:PutObject"],
        Resource = "${aws_s3_bucket.bronze.arn}/*"
      },
      {
        Effect   = "Allow",
        Action   = ["kafka:DescribeCluster","kafka:GetBootstrapBrokers","kafka:WriteData"],
        Resource = data.aws_msk_cluster.kafka.arn
      }
    ]
  })
}
