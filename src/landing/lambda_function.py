import os
import json
import time
import logging
import boto3
from kafka import KafkaProducer

s3 = boto3.client("s3")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
producer = None

def get_producer():
    global producer
    if producer is None:
        brokers = os.environ["KAFKA_BOOTSTRAP_SERVERS"].split(",")
        producer = KafkaProducer(
            bootstrap_servers=brokers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            security_protocol=os.environ.get("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT")
        )
    return producer

def lambda_handler(event, context):
    record = event["Records"][0]["s3"]
    landing_bucket = record["bucket"]["name"]
    landing_key = record["object"]["key"]
    logger.info(f"Processing s3://{landing_bucket}/{landing_key}")
    resp = s3.get_object(Bucket=landing_bucket, Key=landing_key)
    raw = resp["Body"].read().decode("utf-8")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {"raw": raw}
    enriched = {
        "data": payload,
        "metadata": {
            "ingest_time": int(time.time() * 1000),
            "source_name": os.environ["SOURCE_NAME"]
        }
    }
    bronze_bucket = os.environ["BRONZE_BUCKET"]
    bronze_key = f"{landing_key}.json"
    logger.info(f"Writing enriched record to s3://{bronze_bucket}/{bronze_key}")
    s3.put_object(
        Bucket=bronze_bucket,
        Key=bronze_key,
        Body=json.dumps(enriched).encode("utf-8"),
        ContentType="application/json"
    )
    topic = os.environ["KAFKA_TOPIC"]
    logger.info(f"Producing enriched record to Kafka topic '{topic}'")
    prod = get_producer()
    prod.send(topic, enriched)
    prod.flush()
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Processed",
            "bronze_key": bronze_key,
            "kafka_topic": topic
        })
    }
