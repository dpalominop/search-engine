import os
from typing import Optional, List

import logging
import base64

from celery import Celery, states
from fastapi import FastAPI, APIRouter, UploadFile, File, Form, Depends
from pydantic import BaseModel

from src.utils import get_app
from src.config import BROKER_URL, REDIS_URL, LOG_LEVEL
from src.controller.utils import as_form


logging.getLogger("haystack").setLevel(LOG_LEVEL)
logger = logging.getLogger("haystack")

router = APIRouter()
app: FastAPI = get_app()
tasks = Celery(broker=BROKER_URL, backend=REDIS_URL)


@as_form
class FileConverterParams(BaseModel):
    remove_numeric_tables: Optional[bool] = None
    valid_languages: Optional[List[str]] = None


@as_form
class PreprocessorParams(BaseModel):
    clean_whitespace: Optional[bool] = None
    clean_empty_lines: Optional[bool] = None
    clean_header_footer: Optional[bool] = None
    split_by: Optional[str] = None
    split_length: Optional[int] = None
    split_overlap: Optional[int] = None
    split_respect_sentence_boundary: Optional[bool] = None


class Response(BaseModel):
    file_id: str


@router.post("/file-upload")
def upload_file(
    files: List[UploadFile] = File(...),
    # JSON serialized string
    meta: Optional[str] = Form("null"),  # type: ignore
    fileconverter_params: FileConverterParams = Depends(FileConverterParams.as_form),  # type: ignore
    preprocessor_params: PreprocessorParams = Depends(PreprocessorParams.as_form),  # type: ignore
):
    """
    Upload files for indexing.
    """
    logging.info(f"Preparing documents for indexing.")
    enc_files = []
    for file in files:
        try:
            enc_file = base64.b64encode(file.file.read()).decode('utf-8')
            enc_files.append(enc_file)
        finally:
            file.file.close()
        
    payload = {"files": [enc_file for enc_file in enc_files], 
               "filenames": [file.filename for file in files], 
               "meta": meta,
               "fileconverter_params": fileconverter_params.dict(), 
               "preprocessor_params": preprocessor_params.dict()}
    
    logging.info(f"Sending {len(files)} documents to indexing task.")
    task = tasks.send_task(name="indexing", kwargs=payload, queue="indexer")
    logging.info(f"Indexing task sent.")

    return {"task_id": task.id}
