# Machine Learning Batch Schedulling with Prefect and MLFlow

Schedule a ml batch process with prefect and mlflow to process datasets on a monthly basis

## Ingredients
- AWS account
- S3 storage
- Dataset: NY Taxi trip data
  https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page  
  Example: https://s3.amazonaws.com/nyc-tlc/trip+data/green_tripdata_2021-01.parquet  
- MlFlow python library
- Prefect python library
- MLFlow experiment tracked with model saved as artifact. Experiment artifacts have been stored in S3. MLFlow server is not needed for inference.
- Python 3.9 already installed in the host
  - Other libraries:
    - prefect==2.0b6  
    - mlflow
    - scikit-learn==1.0.2
    - pandas
    - pyarrow
    - boto3
    - s3fs

## Important notes

At the time of developing this recipe, Prefect2.0b stores the results of each task in the database of prefect orion. 
This means around 100-200Mb per execution.
In order to avoid this features, any task should write the output to an external file and the next task in the pipeline should read from it.  
This is not implemented here.  

## Setup

### AWS
Create AWS credentials files under C:\Users\<USERNAME>\.aws\
- config
- credentials

These files can by generated with AWS CLI tool by running `aws configure` 
https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

Create an S3 bucket in AWS.
https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html  

### Python environment
```bash
pip install -U pip
pip install pipenv 
pipenv install --dev
shell pipenv
```

## Script explanation
- Load features from S3
- Process features
- Load model from S3 with mlflow. Parameters are experiment uri (S3 uri) and run_id  
  The model is an scikit-learn pipeline with the DictVectorizer and the Regressor
- Make predictions
  We call directly the predict method on the model with the dictionaries of the features.
- Process predictions
- Write output to S3

Examples of input parameters::
  taxi_type = 'green'
  year = '2021'
  month = '2'
  run_id = '6574d0d7c4b044f585c08de11b3582c4'
  experiment_uri = 's3://mlops-bucket-mmjd/2'
  output_uri = 's3://mlops-bucket-mmjd/batch'

run_id is the run_id of the MLFlow experiment that has been tracked.

## Development

### Run prefect orion local server

Run in another terminal:
```bash
prefect orion start
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

### Run the flow manually

```bash
python score.py green 2021 2 <your_run_id> <your_experiment_uri_at_S3> <output_uri_at_S3>
```
Check the Flow run at http://127.0.0.1/4200

Check the bucket with:
```bash
aws s3 ls s3://<name_of_the_bucket>/batch/
```

### Create prefect local storage for deployment

Storage is used to set how flow code for deployments, task results, and flow results are persisted.  

Select 3 (local storage)
./prefect_deployment_storage as the path
Give it a name
Set as default (Y)
Keep the id

Set this id in the script score_deploy.py

### Create the prefect deployment

```bash
prefect deployment create score_deploy.py
```

### Create a prefect queue

Goto prefect orion UI at http://127.0.0.1:4200
Create a Work Queue
  Name: batch_prediction_ny_taxi_queue
  Flow Runners: Subprocess
  Deployments: ml_batch_ny_taxi_prediction
Keep the queue id. E.g. 806931fb-3794-4471-a812-cec96fe3846d

### Start prefect local agent

Local agent will be waiting for works in the queue to be processed. 
When a job is queuing, it will execute the flow (and get the scripts from the storage)

```bash
prefect agent start 806931fb-3794-4471-a812-cec96fe3846d
```

### Schedule a flow run manually

Go to prefect orion ui, open the deployment and click on Run.
The execution will fail since current date does not have a related dataset to download for the current date (now).

## Run backfill processing

Check score_backfill.py and execute
```bash
python score_backfill.py
```

## Todo
- Use remote prefect server
- Set S3 as default storage for deployments 