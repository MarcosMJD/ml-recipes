# Test AWS services (S3) with localstack and pytest

- Simulate a batch model prediction that reads features data from S3 and writes the predictions to S3
- Test this process with a test dataset by running a script that will:
  - Launch localstack container
  - Run pytest to execute integration_test script
  - integration_test sctipt will
    - Create a test dataset and store it in S3 bucket
    - Execute batch prediction over this dataset
    - Compare results

## Ingredients

  - Docker
  - Script to test 
  - Test script
  - Python 3.9:
    - pandas
    - pyarrow
    - s3fs
    - pytest


## Setup
```bash
pip install -U pip
pip install pipenv
pipenv install
shell pipenv
```

## Run test

Run './test/run_test.sh' script from project folder with gitbash
Note: Gitbash must have been setup to be able to run python

```bash
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


if [ ${ERROR_CODE} != 0 ]; then
    docker-compose down --volumes
    exit ${ERROR_CODE}
fi

docker-compose down --volumes
```
