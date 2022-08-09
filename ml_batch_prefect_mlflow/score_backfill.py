from datetime import datetime
from dateutil.relativedelta import relativedelta

from prefect import flow

import score

start_date = datetime(year=2021, month=4, day=1)
end_date = datetime(year=2021, month=6, day=1)
experiment_uri = 's3://mlops-bucket-mmjd/2'
run_id = '6574d0d7c4b044f585c08de11b3582c4'
output_uri = 's3://mlops-bucket-mmjd/batch'
taxi_type = 'green'

# For each loop, prefect will create a task.
# For each loop, prefect will call apply_model which will create a subflow with 5 tasks
@flow
def score_backfill():
    run_date = start_date
    while run_date < end_date:
        score.apply_model (
          experiment_uri = experiment_uri,
          run_id = run_id,
          taxi_type = taxi_type,
          output_uri = output_uri,
          run_date = run_date)
        run_date = run_date + relativedelta(months=1)

if __name__ == '__main__':
    score_backfill()
