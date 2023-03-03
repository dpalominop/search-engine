import os
import json
import uuid
import base64
from pathlib import Path
from typing import Any, Dict, List
import tempfile
import s3fs

from celery import Celery
from celery.utils.log import get_logger
from haystack import Pipeline
from haystack.nodes import BaseConverter, PreProcessor

from src.utils import get_pipelines
from src.config import get_es_handler


BUCKET_NAME = os.getenv("BUCKET_NAME", "")
S3_HOST = os.getenv("S3_HOST", "")

logger = get_logger(name=__name__)
logger.addHandler(get_es_handler())

indexer = Celery(
    "indexer", broker=os.getenv("BROKER_URL"), backend=os.getenv("REDIS_URL")
)
indexing_pipeline: Pipeline = get_pipelines().get("indexing_pipeline", None)


@indexer.task(bind=True, name="indexing")
def indexer_task(self, **kwargs) -> Dict[str, Any]:
    """
    Run filtering task based on input parameters.
    Args:
        kwargs: Input parameter (e.g.: filter params, augmentation_config, etc)
    Return:
        dict: Dictionary including s3_target.
    """
    # if not indexing_pipeline:
    #     raise HTTPException(status_code=501, detail="Indexing Pipeline is not configured.")
    logger.info(f"Indexing task started")
    
    logger.info(f"Uploading files to S3 ...")
    s3 = s3fs.S3FileSystem(client_kwargs={"endpoint_url": f"http://{S3_HOST}:4566"})
    for file, filename in zip(kwargs["files"], kwargs["filenames"]):
        with s3.open(f"s3://{BUCKET_NAME}/{filename}", "wb") as meta_f:
            meta_f.write(base64.decodebytes(file.encode('utf-8')))

    logger.info(f"Files uploaded to S3.")
    
    logger.info(f"Indexing documents ...")
    file_paths: list = []
    file_metas: list = []

    meta_form = json.loads(kwargs["meta"]) or {}  # type: ignore
    # if not isinstance(meta_form, dict):
    #     raise HTTPException(status_code=500, detail=f"The meta field must be a dict or None, not {type(meta_form)}")

    # Create a temporary directory
    tmpdir = tempfile.mkdtemp()
    
    for file, filename in zip(kwargs["files"], kwargs["filenames"]):
        file_path = Path(tmpdir) / f"{uuid.uuid4().hex}_{filename}"
        with file_path.open("wb") as buffer:
            buffer.write(base64.decodebytes(file.encode('utf-8')))

        file_paths.append(file_path)
        meta_form["name"] = filename
        file_metas.append(meta_form)

    # Find nodes names
    converters = indexing_pipeline.get_nodes_by_class(BaseConverter)
    preprocessors = indexing_pipeline.get_nodes_by_class(PreProcessor)

    params = {}
    for converter in converters:
        params[converter.name] = kwargs["fileconverter_params"]
    for preprocessor in preprocessors:
        params[preprocessor.name] = kwargs["preprocessor_params"]

    indexing_pipeline.run(file_paths=file_paths, meta=file_metas, params=params)
    
    logger.info(f"Documents indexed.")

    return {"file_paths": [str(f) for f in file_paths], "meta": file_metas, "params": params}
