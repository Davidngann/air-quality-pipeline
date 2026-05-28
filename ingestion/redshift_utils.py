import os
import psycopg2
from dotenv import load_dotenv
from ingestion.logger import get_logger
from ingestion.exceptions import RedshiftUtilsError

load_dotenv(override=True)
logger = get_logger(__name__)


def get_connection():
    """
    Return a psycopg2 connection to Redshift Serverless.
    Caller is responsible for closing the connection.
    """
    return psycopg2.connect(
        host = os.environ["REDSHIFT_HOST"],
        port=int(os.environ.get("REDSHIFT_PORT", 5439)),
        dbname=os.environ.get("REDSHIFT_DB", "dev"),
        user=os.environ["REDSHIFT_USER"],
        password=os.environ["REDSHIFT_PASSWORD"],
        sslmode="require",
        connect_timeout=90
    )


def run_query(sql: str) -> list[tuple]:
    """
    Execute a SELECT query and return all rows.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            logger.info(f"Running Query: {sql[:50]}...")
            cur.execute(sql)
            rows = cur.fetchall()
            logger.info(f"Returned {len(rows)} rows")
            return rows
    except Exception as e:
        msg = f"Query failed: {e}"
        logger.error(msg)
        raise RedshiftUtilsError(msg)

    finally:
        if conn:
            conn.close()



def execute(sql: str) -> None:
    """
    Execute a non-SELECT statement (INSERT, UPDATE, DDL).
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            logger.info(f"Executing query: {sql[:50]}...")
            cur.execute(sql)
        conn.commit()
        logger.info(f"Execution successful")
    except Exception as e:
        msg = f"Execution failed: {e}"
        logger.error(msg)
        raise RedshiftUtilsError(msg)

    finally:
        if conn:
            conn.close()
