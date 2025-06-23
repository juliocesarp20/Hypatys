import os


class KafkaSettings:
    def __init__(self):
        self.KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "")
        self.KAFKA_CLIENT_ID = os.getenv("KAFKA_CLIENT_ID", "")
        self.KAFKA_SECURITY_PROTOCOL = os.getenv("KAFKA_SECURITY_PROTOCOL", "")
        self.KAFKA_SASL_MECHANISM = os.getenv("KAFKA_SASL_MECHANISM", None)
        self.KAFKA_SASL_USERNAME = os.getenv("KAFKA_SASL_USERNAME", None)
        self.KAFKA_SASL_PASSWORD = os.getenv("KAFKA_SASL_PASSWORD", None)
