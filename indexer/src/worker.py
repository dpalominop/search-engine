import os
import traceback
import json
import shutil
import uuid
import base64
from pathlib import Path
from typing import Any, Dict, List

# import s3fs
from celery import Celery, states
from celery.exceptions import Ignore
from celery.utils.log import get_logger
from haystack import Pipeline
from haystack.nodes import BaseConverter, PreProcessor

from src.utils import get_pipelines
from src.config import FILE_UPLOAD_PATH

# import albumentations as A
# import cv2

# from app.database import filter_products

# BUCKET_NAME = os.getenv("BUCKET_NAME", "")
# DATA_FOLDER = os.getenv("DATA_FOLDER", "")
# S3_HOST = os.getenv("S3_HOST", "")

logger = get_logger(__name__)
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

    file_paths: list = []
    file_metas: list = []

    meta_form = json.loads(kwargs["meta"]) or {}  # type: ignore
    # if not isinstance(meta_form, dict):
    #     raise HTTPException(status_code=500, detail=f"The meta field must be a dict or None, not {type(meta_form)}")

    for file, filename in zip(kwargs["files"], kwargs["filenames"]):
        # try:
        file_path = Path(FILE_UPLOAD_PATH) / f"{uuid.uuid4().hex}_{filename}"
        with file_path.open("wb") as buffer:
            # shutil.copyfileobj(base64.b64decode(file), buffer)
            buffer.write(base64.b64decode(file.encode('utf-8')))

        file_paths.append(file_path)
        meta_form["name"] = filename
        file_metas.append(meta_form)
        # finally:
        #     file.file.close()

    # Find nodes names
    converters = indexing_pipeline.get_nodes_by_class(BaseConverter)
    preprocessors = indexing_pipeline.get_nodes_by_class(PreProcessor)

    params = {}
    for converter in converters:
        params[converter.name] = kwargs["fileconverter_params"]
    for preprocessor in preprocessors:
        params[preprocessor.name] = kwargs["preprocessor_params"]

    indexing_pipeline.run(file_paths=file_paths, meta=file_metas, params=params)

    # return {"s3_target": s3_target}
