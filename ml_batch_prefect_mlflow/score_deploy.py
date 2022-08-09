from prefect.deployments import DeploymentSpec
from prefect.orion.schemas.schedules import CronSchedule
from prefect.flow_runners import SubprocessFlowRunner

# Check https://crontab.guru/ for the cron schedule
# Check https://orion-docs.prefect.io/concepts/deployments/

experiment_uri = 's3://mlops-bucket-mmjd/2'
run_id = '6574d0d7c4b044f585c08de11b3582c4'
output_uri = 's3://mlops-bucket-mmjd/batch'
taxi_type = 'green'

DeploymentSpec(
    flow_location="score.py",
    name="ml_batch_ny_taxi_prediction",
    schedule=CronSchedule(cron="0 3 2 * *"),
    flow_runner=SubprocessFlowRunner(),
    #flow_storage='47783921-a304-4378-95ee-e03a056b0385',
    tags=["ml_batch_ny_taxi"],
    parameters = {
        experiment_uri: experiment_uri,
        run_id: run_id,
        taxi_type: taxi_type,
        output_uri: output_uri,
    }
)
