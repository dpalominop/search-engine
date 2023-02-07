import os
from pathlib import Path


PIPELINE_YAML_PATH = os.getenv(
    "PIPELINE_YAML_PATH", str((Path(__file__).parent / "pipeline" / "pipelines.haystack-pipeline.yml").absolute())
)
QUERY_PIPELINE_NAME = os.getenv("QUERY_PIPELINE_NAME", "query")

FILE_UPLOAD_PATH = os.getenv("FILE_UPLOAD_PATH", str((Path(__file__).parent / "file-upload").absolute()))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ROOT_PATH = os.getenv("ROOT_PATH", "/")

CONCURRENT_REQUEST_PER_WORKER = int(os.getenv("CONCURRENT_REQUEST_PER_WORKER", "4"))

BUCKET_NAME = os.getenv("BUCKET_NAME", "")
S3_HOST = os.getenv("S3_HOST", "")

BROKER_URL=os.getenv("BROKER_URL")
REDIS_URL=os.getenv("REDIS_URL")
