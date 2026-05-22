import boto3
import pytest
from moto import mock_aws

MOCK_BUCKET = "test-bucket"
MOCK_REGION = "ap-southeast-2"

@pytest.fixture
def aws_credentials(monkeypatch):
    """
    Mocked AWS Credentials so moto intercept correctly
    """
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", MOCK_REGION)

@pytest.fixture
def s3_bucket(aws_credentials):
    """
    Create a mock s3 bucket for testing
    """
    with mock_aws():
        boto3.client("s3", region_name = MOCK_REGION).create_bucket(
            Bucket = MOCK_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": MOCK_REGION}
        )
        yield MOCK_BUCKET
        