from ingestion.logger import get_logger
import boto3
from dotenv import load_dotenv
from ingestion.exceptions import S3UtilsError

load_dotenv(override=True)
logger = get_logger(__name__)

def _get_client():
    return boto3.client("s3")

def upload_file(local_file_path: str, bucket: str, s3_key: str) -> None:
    """
    Upload a local file to s3 bucket at the given key
    """
    if not s3_key:
        msg = f"s3 key is needed"
        logger.error(msg)
        raise S3UtilsError(msg)
    try:
        logger.info(f"Uploading started: {local_file_path} -> s3://{bucket}/{s3_key}")
        _get_client().upload_file(local_file_path, bucket, s3_key)
        logger.info("upload success")
    except Exception as e:
        msg = f"Failed to upload file to S3: {e}"
        logger.error(msg, exc_info=True)
        raise S3UtilsError(msg)

def list_objects(bucket:str, prefix: str) -> list[str]:
    """
    Return a list of all object keys under the given prefix
    """
    try:
        logger.info(f"Object list from bucket: {bucket} with prefix: {prefix}")
        keys = []
        paginator = _get_client().get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                keys.append(obj["Key"])
        return keys
    except Exception as e:
        msg = f"Failed to list object from bucket: {bucket} with prefix: {prefix} with error: {e}"
        logger.error(msg, exc_info=True)
        raise S3UtilsError(msg)



def download_file(bucket: str, s3_key: str, local_path: str) -> None:
    """
    Download an s3 object to a local path
    """
    try:
        logger.info(f"download started from s3://{bucket}/{s3_key} -> local: {local_path} ")
        _get_client().download_file(bucket, s3_key, local_path)
        logger.info("download success")
    except Exception as e:
        msg = f"Failed to download file from s3://{bucket}/{s3_key} with error: {e}"
        logger.error(msg, exc_info=True)
        raise S3UtilsError(msg)
