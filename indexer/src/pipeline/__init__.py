from typing import Any, Dict

import os
import logging
from pathlib import Path

from contextlib import contextmanager
from threading import Semaphore

from fastapi import HTTPException

from haystack.pipelines.base import Pipeline
from haystack.document_stores import FAISSDocumentStore, InMemoryDocumentStore
from haystack.errors import PipelineConfigError


class RequestLimiter:
    def __init__(self, limit):
        self.semaphore = Semaphore(limit)

    @contextmanager
    def run(self):
        acquired = self.semaphore.acquire(blocking=False)
        if not acquired:
            raise HTTPException(status_code=503, detail="The server is busy processing requests.")
        try:
            yield acquired
        finally:
            self.semaphore.release()



logger = logging.getLogger(__name__)

# Each instance of FAISSDocumentStore creates an in-memory FAISS index,
# the Indexing & Query Pipelines will end up with different indices for each worker.
# The same applies for InMemoryDocumentStore.
SINGLE_PROCESS_DOC_STORES = (FAISSDocumentStore, InMemoryDocumentStore)


def _load_pipeline(pipeline_yaml_path, indexing_pipeline_name):
    # Load pipeline (if available)
    try:
        pipeline = Pipeline.load_from_yaml(Path(pipeline_yaml_path), pipeline_name=indexing_pipeline_name)
        logging.info("Loaded pipeline nodes: %s", pipeline.graph.nodes.keys())
        document_store = _get_pipeline_doc_store(pipeline)
    except PipelineConfigError as e:
        pipeline, document_store = None, None
        logger.error(
            "Error loading %s pipeline from %s. \n %s\n", indexing_pipeline_name, pipeline_yaml_path, e.message
        )
    return pipeline, document_store


def _get_pipeline_doc_store(pipeline):
    document_store = pipeline.get_document_store()
    logging.info("Loaded docstore: %s", document_store)
    if isinstance(document_store, SINGLE_PROCESS_DOC_STORES):
        logger.warning("FAISSDocumentStore or InMemoryDocumentStore should only be used with 1 worker.")
    return document_store


def setup_pipelines() -> Dict[str, Any]:
    # Re-import the configuration variables
    from src.config import CONFIG # pylint: disable=reimported

    pipelines = {}

    # Setup concurrency limiter
    concurrency_limiter = RequestLimiter(CONFIG.CONCURRENT_REQUEST_PER_WORKER)
    logging.info("Concurrent requests per worker: %s", CONFIG.CONCURRENT_REQUEST_PER_WORKER)
    pipelines["concurrency_limiter"] = concurrency_limiter

    print("CONFIG.PIPELINE_YAML_PATH: ", CONFIG.PIPELINE_YAML_PATH, CONFIG.INDEXING_PIPELINE_NAME)
    # Load indexing pipeline
    index_pipeline, _ = _load_pipeline(CONFIG.PIPELINE_YAML_PATH, CONFIG.INDEXING_PIPELINE_NAME)
    if not index_pipeline:
        logger.warning("Indexing Pipeline is not setup. File Upload API will not be available.")
    pipelines["indexing_pipeline"] = index_pipeline

    # Create directory for uploaded files
    os.makedirs(CONFIG.FILE_UPLOAD_PATH, exist_ok=True)

    return pipelines
