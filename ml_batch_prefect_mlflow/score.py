import sys
import uuid
import pandas as pd
import mlflow
from datetime import datetime
from prefect import task, flow, get_run_logger
from prefect.context import get_run_context
from dateutil.relativedelta import relativedelta

@task
def read_dataframe(filename: str):
    
    df = pd.read_parquet(filename)
    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)]
    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)
    df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']
    df['ride_id'] = df.apply(lambda x: str(uuid.uuid4()), axis = 1)
    
    return df

@task
def prepare_dictionaries(df: pd.DataFrame):

    categorical = ['PU_DO']
    numerical = ['trip_distance']
    dicts = df[categorical + numerical].to_dict(orient='records')

    return dicts

@task
def load_model(logged_model):

    model = mlflow.pyfunc.load_model(logged_model)
    return model

@task
def make_result (df, y_pred, model_version):
    
    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['lpep_pickup_datetime'] = df['lpep_pickup_datetime']
    df_result['PULocationID'] = df['PULocationID']
    df_result['DOLocationID'] = df['DOLocationID']
    df_result['actual_duration'] = df['duration']
    df_result['predicted_duration'] = y_pred
    df_result['diff'] = df_result['actual_duration'] - df_result['predicted_duration']
    df_result['model_version'] = model_version

    return df_result

def get_path_files(run_date, taxi_type, run_id, output_uri):

    if run_date is None:
        ctx = get_run_context()
        run_date = ctx.flow_run.expected_start_time

    prev_month = run_date - relativedelta(months=1)
    year = prev_month.year
    month = prev_month.month
    input_file = (
        f's3://nyc-tlc/trip data/'
        f'{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet')
    output_file = f'{output_uri}/{taxi_type}-{year:04d}-{month:02d}-{run_id}.parquet'

    return input_file, output_file

@task
def make_prediction(model, dicts):
    y_pred = model.predict(dicts)
    return y_pred

@flow
def apply_model (
    experiment_uri: str,
    run_id: str,
    taxi_type: str,
    output_uri: str,
    run_date: datetime = None):

    logger = get_run_logger()
    logger.info('Running batch processing with the following parameters:')
    logger.info(f'taxi_type = {taxi_type}')
    logger.info(f'run_date = {run_date}')
    logger.info(f'experiment_uri = {experiment_uri}')
    logger.info(f'run_id = {run_id}')
    logger.info(f'output_uri = {output_uri}')

    input_file, output_file = get_path_files(run_date, taxi_type, run_id, output_uri)

    logged_model = f'{experiment_uri}/{run_id}/artifacts/model'
    df = read_dataframe(input_file).result()
    dicts = prepare_dictionaries(df).result()
    model = load_model(logged_model).result()
    y_pred = make_prediction(model, dicts).result()
    df_result = make_result(df, y_pred, run_id).result()
    df_result.to_parquet(output_file)


def run():

    taxi_type = sys.argv[1] if len(sys.argv) > 1 else 'green'
    year = int(sys.argv[2]) if len(sys.argv) > 2 else 2021
    month = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    experiment_uri = sys.argv[4] if len(sys.argv) > 4 else 's3://mlops-bucket-mmjd/2'
    run_id = sys.argv[5] if len(sys.argv) > 5 else '6574d0d7c4b044f585c08de11b3582c4'
    output_uri = sys.argv[6] if len(sys.argv) > 6 else 's3://mlops-bucket-mmjd/batch'

    print('Running batch processing with the following parameters:')
    print(f'taxi_type = {taxi_type}')
    print(f'year = {year}')
    print(f'month = {month}')
    print(f'experiment_uri = {experiment_uri}')
    print(f'run_id = {run_id}')
    print(f'output_uri = {output_uri}')

    apply_model (
       experiment_uri = experiment_uri,
       run_id = run_id,
       taxi_type = taxi_type,
       output_uri = output_uri,
       run_date = datetime(year=year, month=month, day=1))

if __name__ == '__main__':
    run()
