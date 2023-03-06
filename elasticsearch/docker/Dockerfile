FROM docker.elastic.co/elasticsearch/elasticsearch:7.17.6

COPY ./requirements.txt requirements.txt

RUN apt-get update -yqq && \
    apt-get install -y python3-pip

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./logging-template.py logging-template.py
