import uvicorn
from src.utils import get_app, get_pipelines
from src.config import get_logger


logger = get_logger(name="api")

app = get_app()
pipelines = get_pipelines()  # Unused here, called to init the pipelines early


logger.info("Open http://127.0.0.1:8000/docs to see Swagger API Documentation.")
logger.info(
    "Or just try it out directly: curl --request POST --url 'http://127.0.0.1:8000/query' "
    '-H "Content-Type: application/json"  --data \'{"query": "Who is the father of Arya Stark?"}\''
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
