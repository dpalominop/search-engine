ARG base_image_tag
ARG base_image

FROM ${base_image}:${base_image_tag}

COPY /requirements.txt /tmp/requirements.txt

ENV APP_DIR='/app'
WORKDIR $APP_DIR

RUN apt-get update -yqq && \
    apt-get -yqq install libsndfile1 --no-install-recommends && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --compile -r /tmp/requirements.txt && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/* /tmp/* /var/tmp/*

ADD /src $APP_DIR/src/
# ADD worker.py $APP_DIR/

EXPOSE 6379 5672
