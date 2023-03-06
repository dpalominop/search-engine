#!/bin/sh
echo "Init localstack s3"
# bucket to store imagery data
# can be used to store initial imagery
awslocal s3 mb s3://document-datasets
# bucket to store tasks results
awslocal s3 mb s3://document-tasks

#awslocal s3 sync /tmp/localstack/dataset s3://document-datasets/dataset-v1
