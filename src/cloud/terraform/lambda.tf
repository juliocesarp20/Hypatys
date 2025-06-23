data "aws_msk_cluster" "kafka" {
  cluster_name = var.kafka_cluster_name
}

data "aws_subnet" "kafka_subnet" {
  id = tolist(
    data.aws_msk_cluster.kafka
      .broker_node_group_info[0]
      .client_subnets
  )[0]
}

locals {
  vpc_id        = data.aws_subnet.kafka_subnet.vpc_id
  kafka_subnets = tolist(
    data.aws_msk_cluster.kafka
      .broker_node_group_info[0]
      .client_subnets
  )
  kafka_sg_ids  = tolist(
    data.aws_msk_cluster.kafka
      .broker_node_group_info[0]
      .security_groups
  )
}


resource "aws_security_group" "lambda_sg" {
  name   = "lambda-landing-sg"
  vpc_id = local.vpc_id

  egress {
    from_port   = 9092
    to_port     = 9092
    protocol    = "tcp"
    cidr_blocks = []
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "lambda-landing-sg"
  }
}

resource "aws_security_group_rule" "allow_lambda_to_msk" {
  type                     = "ingress"
  from_port                = 9092
  to_port                  = 9092
  protocol                 = "tcp"
  security_group_id        = local.kafka_sg_ids[0]
  source_security_group_id = aws_security_group.lambda_sg.id
  description              = "Allow Lambda to talk to MSK"
}

data "archive_file" "landing_processor_zip" {
  type        = "zip"
  source_file = "${path.module}/../../landing/lambda_function.py"
  output_path = "${path.module}/landing_processor.zip"
}

resource "aws_lambda_function" "landing_processor" {
  function_name    = "landing-processor-prd"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.9"
  filename         = data.archive_file.landing_processor_zip.output_path
  source_code_hash = data.archive_file.landing_processor_zip.output_base64sha256

  vpc_config {
    subnet_ids         = local.kafka_subnets
    security_group_ids = [ aws_security_group.lambda_sg.id ]
  }

  environment {
    variables = {
      BRONZE_BUCKET           = aws_s3_bucket.bronze.bucket
      SOURCE_NAME             = aws_s3_bucket.landing.bucket
      KAFKA_BOOTSTRAP_SERVERS = data.aws_msk_cluster.kafka.bootstrap_brokers
      KAFKA_TOPIC             = "landing-events"
      KAFKA_SECURITY_PROTOCOL = "PLAINTEXT"
      KAFKA_CLUSTER_ARN       = data.aws_msk_cluster.kafka.arn
    }
  }
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.landing_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.landing.arn
}
