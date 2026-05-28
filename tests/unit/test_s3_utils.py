from ingestion.s3_utils import upload_file, download_file, list_objects
import boto3
from tests.conftest import MOCK_REGION, MOCK_BUCKET
from ingestion.exceptions import S3UtilsError, RedshiftUtilsError
import pytest

def test_upload_file_success(s3_bucket, tmp_path):
    """Upload a file and verify it exists in S3."""
    local_file = tmp_path / "test.json"
    local_file.write_text('{"value": 1}')
    s3_key = "raw/historical/year=2024/month=01/test.json"

    upload_file(str(local_file), s3_bucket, s3_key)

    client = boto3.client("s3", region_name=MOCK_REGION)
    response = client.list_objects_v2(Bucket=MOCK_BUCKET, Prefix=s3_key)
    assert response["KeyCount"] == 1
    assert response["Contents"][0]["Key"] == s3_key

def test_upload_file_missing_key_raises(s3_bucket, tmp_path):
    """upload_file with empty s3_key raises S3UtilsError."""
    local_file = tmp_path / "test.json"
    local_file.write_text('{"value": 1}')
    with pytest.raises(S3UtilsError, match="s3 key is needed"):
        upload_file(str(local_file), s3_bucket, '')


def test_list_objects_returns_keys(s3_bucket, tmp_path):
    """Upload two files, list by prefix, verify both keys returned."""

    local_file_1 = tmp_path / "test.json"
    local_file_1.write_text('{"value": 1}')
    s3_key_1 = "raw/historical/year=2024/month=01/test.json"

    local_file_2 = tmp_path / "test_2.json"
    local_file_2.write_text('{"value": 2}')
    s3_key_2 = "raw/historical/year=2024/month=02/test_2.json"

    upload_file(str(local_file_1), s3_bucket, s3_key_1)
    upload_file(str(local_file_2), s3_bucket, s3_key_2)

    keys = list_objects(s3_bucket, "raw/historical/year=2024")
    assert len(keys) == 2
    assert s3_key_1 in keys
    assert s3_key_2 in keys

def test_list_objects_empty_prefix_returns_empty(s3_bucket):
    """list_objects on a prefix with no objects returns empty list."""
    keys = list_objects(s3_bucket, "non-existing-prefix")
    assert len(keys) == 0

def test_download_file_success(s3_bucket, tmp_path):
    """Upload a file, download it, verify contents match."""

    text = '{"value": 1}'
    local_file = tmp_path / "test.json"
    local_file.write_text(text)
    s3_key = "raw/historical/year=2024/month=01/test.json"

    upload_file(str(local_file), s3_bucket, s3_key)

    local_output_filename = tmp_path / "result.json"
    download_file(s3_bucket, s3_key, str(local_output_filename))

    assert local_output_filename.is_file()
    assert local_output_filename.read_text() == text