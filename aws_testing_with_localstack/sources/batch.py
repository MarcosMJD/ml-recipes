import pandas as pd
import uuid
import os

class DummyModel:

    def __init__(self, version: str = '1.0'):
        self.version = version
        return

    def predict(self, features: pd.DataFrame):
        df = pd.DataFrame()
        df['prediction'] = features['f1'] + features['f2']
        df['id'] = features['id']
        return df

class ModelService:

    def __init__(self, model: DummyModel):

        self.model = model

    def preprocess_features(self, data: pd.DataFrame):

        data['id'] = data.apply(lambda x: str(uuid.uuid4()), axis = 1)
        return data

    def predict(self, features: pd.DataFrame):

        pred = self.model.predict(features)
        return pred

def read_data(url: str, options):

    df = pd.read_parquet(url, storage_options=options)
    return df

def write_data(url: str, data: pd.DataFrame, options):

    data.to_parquet(url,engine='pyarrow', index=False, storage_options=options)


if __name__ == "__main__":

    bucket = os.getenv('BUCKET', 'test_buquet')
    filename_features = os.getenv('FEATURES_FILE', 'features.parquet')
    filename_predictions = os.getenv('PREDICTIONS_FILE', 'predictions.parquet')
    url_data_in = f's3://{bucket}/{filename_features}'
    url_data_out = f's3://{bucket}/{filename_predictions}'

    print(bucket)
    print(url_data_in)
    print(url_data_out)

    s3_endpoint_url = os.getenv('S3_ENDPOINT')
    if (s3_endpoint_url) is not None:
        options = {
            'client_kwargs': {
                'endpoint_url': s3_endpoint_url
            }
        }
    else:
        options = None

    data_in = read_data(url_data_in, options)
    model = DummyModel('v1')
    model_service = ModelService(model)
    print (data_in)
    features = model_service.preprocess_features(data_in)
    print(features)
    predictions = model_service.predict(features)
    print(predictions)
    write_data(url_data_out, predictions, options)

