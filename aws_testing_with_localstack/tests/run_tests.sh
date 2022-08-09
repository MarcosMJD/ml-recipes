#!/usr/bin/env bash
cd "$(dirname "$0")"

export BUCKET='test-bucket'
export FEATURES_FILE='features.parquet'
export PREDICTIONS_FILE='predictions.parquet'
export S3_ENDPOINT='http://localhost:4566'

echo ${BUCKET}

# launch localstack
docker-compose up -d

sleep 1

# create aws bucket in localstack
aws --endpoint-url=${S3_ENDPOINT} s3 mb s3://${BUCKET}

# -s shows prints

pytest integration_tests.py -s

ERROR_CODE=$?


#if [ ${ERROR_CODE} != 0 ]; then
#    docker-compose down --volumes
#    exit ${ERROR_CODE}
#fi

#docker-compose down --volumes
