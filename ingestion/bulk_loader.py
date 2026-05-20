import os
import json
import calendar
import tempfile
from datetime import datetime, timezone

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

from ingestion.logger import get_logger
from ingestion.exceptions import BulkLoaderError
from ingestion.s3_utils import upload_file

load_dotenv(override=True)
openaq_api = os.environ["OPENAQ_API_KEY"]
raw_bucket = os.environ["S3_RAW_BUCKET"]
logger = get_logger(__name__)

def build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=2, 
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session

session = build_session()


def fetch_melbourne_locations(
        lat: float,
        lon: float,
        radius_m: int
        ) -> list[dict]:
    """
    Fetch all Melbourne monitoring locations within radius.
    Handles the '>N' pagination quirk.
    Returns list of location dicts including embedded sensors.
    """
    headers = {"X-API-Key": openaq_api,
              "Content-Type": "application/json"}
    base_url = "https://api.openaq.org/v3/locations"
    params = {
        "coordinates": f"{lat},{lon}",
        "radius": radius_m,
        "limit": 100,
        "page": 1
    }
    
    all_results = []
    try:
        while True:
            response = session.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            result = data.get("results", [])
            all_results.extend(result)


            logger.info(f"Fetched page {params['page']}: {len(result)}")

            if not result:
                break

            params["page"] += 1

    except requests.HTTPError as e:
        msg = f"HTTP error fetching locations: {e}"
        logger.error(msg)
        raise BulkLoaderError(msg)
    except Exception as e:
        msg = f"failed to fetch locations: {e}"
        logger.error(msg)
        raise BulkLoaderError(msg)
    
    return all_results


def fetch_sensor_measurements(
    sensor_id: int,
    datetime_from: str,
    datetime_to: str
) -> list[dict]:
    """
    Fetch all measurements for a single sensor within a date range.
    Handles pagination. datetime format: ISO 8601 (2024-03-01T00:00:00Z)
    Returns list of measurement dicts.
    """
    headers = {"X-API-Key": openaq_api,
            "Content-Type": "application/json"}
    base_url = f"https://api.openaq.org/v3/sensors/{sensor_id}/measurements"
    params = {
        "datetime_from": datetime_from,
        "datetime_to": datetime_to,
        "page": 1,
        "limit": 1000,
    }
    
    all_results = []
    logger.info(f"Fetching data from sensor {sensor_id}")
    try:
        while True:
            response = session.get(base_url, params=params, headers=headers)

            response.raise_for_status()
            data = response.json()
            result = data.get("results", [])
            all_results.extend(result)

            logger.info(f"Fetched page {params['page']}: {len(result)}")

            if not result:
                break

            params["page"] += 1

    except requests.HTTPError as e:
        msg = f"HTTP error fetching measurement: {e}"
        logger.error(msg)
        raise BulkLoaderError(msg)
    except Exception as e:
        msg = f"failed to fetch measurement: {e}"
        logger.error(msg)
        raise BulkLoaderError(msg)
    
    return all_results


def build_s3_key(location_id: int, year: int, month: int) -> str:
    """
    Build the S3 partition key for a given location/year/month.
    """
    return f"raw/historical/year={year}/month={month:02d}/location_{location_id}_{year}_{month:02d}.json"

def run_bulk_load(year: int, month: int) -> None:
    """
    Orchestrates the full bulk load for all Melbourne locations
    for a given year and month. One JSON file per location uploaded to S3.
    """

    all_locations = fetch_melbourne_locations(-37.803, 144.981, 5000)
    processed = 0
    skipped = 0

    for location in all_locations:
        datetime_last = location.get("datetimeLast", {}).get("utc")
        if not datetime_last:
            logger.warning(f"No datetimeLast for {location['name']} | Skipped") 
            skipped += 1
            continue

        last_dt = datetime.fromisoformat(datetime_last.replace("Z", "+00:00"))
        cutoff = datetime(year, month, 1, tzinfo=last_dt.tzinfo)
        if last_dt < cutoff:
            logger.info(f"Skipping {location['name']} - last data taken: {last_dt}")
            skipped += 1
            continue

        payload = {
            "location_id": location["id"],
            "location_name": location["name"],
            "locality": location.get("locality"),
            "coordinates": location["coordinates"],
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "year": year,
            "month": month,
            "sensors": []
        }           


        datetime_from = f"{year}-{month:02d}-01T00:00:00Z"
        last_day = calendar.monthrange(year, month)[1]
        # datetime_to = f"{year}-{month:02d}-{last_day}T23:59:59Z"
        datetime_to = f"{year}-{month:02d}-02T23:59:59Z"


        for sensor in location["sensors"]:
            measurements = fetch_sensor_measurements(
                sensor["id"],
                datetime_from=datetime_from,
                datetime_to=datetime_to
            )

            payload["sensors"].append({
                "sensor_id": sensor["id"],
                "parameter": sensor["parameter"]["name"],
                "unit": sensor["parameter"]["units"],
                "measurements": measurements
            })

            logger.info(f"Sensor {sensor['id']} ({sensor['parameter']['name']}): {len(measurements):,} measurements")

        temp_path = None
        
        try:
            with tempfile.NamedTemporaryFile(mode='w',suffix='.json',delete=False) as f:
                json.dump(payload, f)
                temp_path = f.name
                s3_key = build_s3_key(location_id=location["id"], year=year, month=month)
                upload_file(temp_path, raw_bucket, s3_key=s3_key)
                logger.info(f"Uploaded {location['name']} -> {s3_key}")
                processed += 1
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    logger.info(f"Bulk load complete: {year}-{month:02d}: uploaded: {processed:,} | skipped: {skipped:,} ")

