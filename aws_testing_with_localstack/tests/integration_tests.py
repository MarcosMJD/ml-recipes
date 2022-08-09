import pandas as pd
import sys
import os

import sys
# Add parent directory so that sources package can be found. Since this script is called from test directory
sys.path.append('../')

def test_integration():

    bucket = os.getenv('BUCKET', 'test-bucket')
    filename_features = os.getenv('FEATURES_FILE', 'features')
    filename_predictions = os.getenv('PREDICTIONS_FILE', 'predictions')

    url_data_in = f's3://{bucket}/{filename_features}'
    url_data_out = f's3://{bucket}/{filename_predictions}'

    s3_endpoint_url = os.getenv('S3_ENDPOINT')

    if (s3_endpoint_url) is not None:
        options = {
            'client_kwargs': {
                'endpoint_url': s3_endpoint_url
            }
        }
    else:
        options = None

    data = [
      (1,2),
      (3,4)
    ]
    columns = ['f1', 'f2']
    input_df = pd.DataFrame(data, columns=columns)
    input_df.to_parquet(
        url_data_in,
        engine='pyarrow',
        index=False,
        storage_options=options,
    )

    command = 'python ../sources/batch.py'
    os.system(command)

    expected_prediction = 10
    predictions = pd.read_parquet(url_data_out, storage_options=options)
    actual_prediction = predictions['prediction'].sum()

    assert expected_prediction == actual_prediction








