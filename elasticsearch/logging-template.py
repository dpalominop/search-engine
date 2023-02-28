#!/usr/bin/env python3
import logging
import os
import sys

from elasticsearch import Elasticsearch


logging.captureWarnings(True)

elasticsearch = Elasticsearch(
    hosts=os.environ.get('ELASTIC_HOST', 'http://localhost:9200'),
    verify_certs=False,
    http_auth=(
        os.environ.get('ELASTIC_USERNAME', 'elastic'), 
        os.environ.get('ELASTIC_PASSWORD', 'changeme')
        ),
)

if not elasticsearch.ping():
    logging.error('Elasticsearch is not available')
    sys.exit(1)
    

elasticsearch.indices.put_index_template(
    name="logging-template",
    index_patterns=["logging-module-*"],
    template={
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "log_analyzer": {
                        "type": "pattern",
                        "tokenizer": "\\W+",
                        "lowercase": True,
                    }
                },
                "normalizer": {
                    "lowercase_normalizer": {
                        "type": "custom",
                        "filter": ["lowercase"]
                    }
                }
            }
        },    
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "level": {"type": "keyword"},
                "thread": {
                    "type": "text",
                    "analyzer": "log_analyzer",
                    "norms": False,
                    "similarity": "boolean",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "normalizer": "lowercase_normalizer"
                        }
                    }
                },
                "message": {
                    "type": "text",
                    "analyzer": "log_analyzer",
                    "norms": False,
                    "similarity": "boolean"
                }
            }
        }
    }
)
