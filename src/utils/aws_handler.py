import logging
from typing import Optional

import boto3
from pydantic import BaseSettings, Field


class AWSSettings(BaseSettings):
    AWS_ACCESS_KEY_ID: str = Field(..., env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: Optional[str] = Field("us-east-1", env="AWS_REGION")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class AWSHandler:
    def __init__(self):
        self.settings = AWSSettings()
        self.session = boto3.Session(
            aws_access_key_id=self.settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.settings.AWS_SECRET_ACCESS_KEY,
            region_name=self.settings.AWS_REGION,
        )
        self.logger = logging.getLogger(__name__)

    def get_client(self, service_name: str):
        """Get a boto3 client for the specified AWS service."""
        try:
            client = self.session.client(service_name)
            self.logger.info(f"Successfully created client for service: {service_name}")
            return client
        except Exception as e:
            self.logger.error(
                f"Failed to create client for service {service_name}: {e}"
            )
            raise

    def get_resource(self, service_name: str):
        """Get a boto3 resource for the specified AWS service."""
        try:
            resource = self.session.resource(service_name)
            self.logger.info(
                f"Successfully created resource for service: {service_name}"
            )
            return resource
        except Exception as e:
            self.logger.error(
                f"Failed to create resource for service {service_name}: {e}"
            )
            raise
