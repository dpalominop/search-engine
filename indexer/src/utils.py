from src.pipeline import setup_pipelines


pipelines = None


def get_pipelines():
    global pipelines  # pylint: disable=global-statement
    if not pipelines:
        pipelines = setup_pipelines()
    return pipelines
