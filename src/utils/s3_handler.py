import logging

from botocore.exceptions import BotoCoreError, ClientError

from src.utils.aws_handler import AWSHandler

logger = logging.getLogger(__name__)


class S3Handler(AWSHandler):
    def __init__(self):
        super().__init__()
        self.s3_client = self.session.client("s3")

    def upload_file(self, file_path: str, bucket_name: str, object_name: str) -> bool:
        """
        Uploads a file to the specified S3 bucket.

        Args:
            file_path (str): Path to the file to upload.
            bucket_name (str): S3 bucket name.
            object_name (str): S3 object key.

        Returns:
            bool: True if the upload was successful, False otherwise.
        """
        try:
            logger.info(
                f"Uploading {file_path} to bucket {bucket_name} as {object_name}."
            )
            self.s3_client.upload_file(file_path, bucket_name, object_name)
            logger.info("Upload successful.")
            return True
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to upload file: {e}")
            return False

    def download_file(self, bucket_name: str, object_name: str, file_path: str) -> bool:
        """
        Downloads a file from the specified S3 bucket.

        Args:
            bucket_name (str): S3 bucket name.
            object_name (str): S3 object key.
            file_path (str): Local path to save the downloaded file.

        Returns:
            bool: True if the download was successful, False otherwise.
        """
        try:
            logger.info(
                f"Downloading {object_name} from bucket {bucket_name} to {file_path}."
            )
            self.s3_client.download_file(bucket_name, object_name, file_path)
            logger.info("Download successful.")
            return True
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to download file: {e}")
            return False

    def list_bucket_objects(self, bucket_name: str) -> list:
        """
        Lists objects in the specified S3 bucket.

        Args:
            bucket_name (str): S3 bucket name.

        Returns:
            list: A list of object keys in the bucket.
        """
        try:
            logger.info(f"Listing objects in bucket {bucket_name}.")
            response = self.s3_client.list_objects_v2(Bucket=bucket_name)
            objects = [obj["Key"] for obj in response.get("Contents", [])]
            logger.info(f"Found {len(objects)} objects.")
            return objects
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to list objects: {e}")
            return []

    def delete_object(self, bucket_name: str, object_name: str) -> bool:
        """
        Deletes an object from the specified S3 bucket.

        Args:
            bucket_name (str): S3 bucket name.
            object_name (str): S3 object key to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        try:
            logger.info(f"Deleting object {object_name} from bucket {bucket_name}.")
            self.s3_client.delete_object(Bucket=bucket_name, Key=object_name)
            logger.info("Deletion successful.")
            return True
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to delete object: {e}")
            return False
