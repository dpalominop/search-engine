import os
import sys
import logging
from pathlib import Path

from cmreslogging.handlers import CMRESHandler


def get_stream_handler(*, formatter: logging.Formatter) -> logging.StreamHandler:
    """Get a stream handler for the logger.
    Args:
        formatter: The formatter to use for the stream handler.
    Returns:
        logging.StreamHandler: The stream handler.
    """
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    return stream_handler


def get_es_handler(*, formatter: logging.Formatter) -> logging.StreamHandler:
    """Get a ElasticSearch logging handler and adds Elastic common schema formatter.
    Args:
        formatter: The formatter to use for the stream handler.
    Returns:
        logging.StreamHandler: The stream handler.
    """
    es_handler = CMRESHandler(
                    hosts=[{'host': os.getenv("ELASTIC_HOST", "elasticsearch"), 
                            'port': int(os.getenv("ELASTIC_PORT", 9200))}],
                    auth_type=CMRESHandler.AuthType.BASIC_AUTH,
                    auth_details=(os.getenv("ELASTIC_USERNAME", "elastic"), 
                                  os.getenv("ELASTIC_PASSWORD", "changeme")),
                    es_index_name="logging-module-indexer",
                    es_doc_type="document"
                )
    es_handler.setFormatter(formatter)
    return es_handler


def get_logger(name: str) -> logging.Logger:
    """Get a logger with a given name.
    Args:
        name: The name of the logger.
    Returns:
        logging.Logger: The logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    logger.addHandler(get_stream_handler(formatter=logging.Formatter(fmt="%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
                                                                     datefmt="%Y-%m-%d %H:%M:%S")))
    logger.addHandler(get_es_handler(formatter=logging.Formatter(fmt="%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
                                                                 datefmt="%Y-%m-%d %H:%M:%S")))
    return logger


class Config:
    """Configuration for the application."""

    PIPELINE_YAML_PATH = os.getenv(
        "PIPELINE_YAML_PATH", str((Path(__file__).parent / "pipeline" / "pipelines.haystack-pipeline.yml").absolute())
    )
    INDEXING_PIPELINE_NAME = os.getenv("INDEXING_PIPELINE_NAME", "indexing")

    FILE_UPLOAD_PATH = os.getenv("FILE_UPLOAD_PATH", str((Path(__file__).parent / "file-upload").absolute()))

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ROOT_PATH = os.getenv("ROOT_PATH", "/")

    CONCURRENT_REQUEST_PER_WORKER = int(os.getenv("CONCURRENT_REQUEST_PER_WORKER", "4"))

CONFIG = Config()
