import grpc
import requests
from io import BytesIO
import tensorflow as tf
from keras_image_helper import create_preprocessor
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
from PIL import Image

HOST = 'localhost:8500'

CLASSES = [
    'dress',
    'hat',
    'longsleeve',
    'outwear',
    'pants',
    'shirt',
    'shoes',
    'shorts',
    'skirt',
    't-shirt'
]

channel = grpc.insecure_channel(HOST)
stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)


def load_and_preprocess_data(URI):
    preprocessor = create_preprocessor('xception', target_size=(299, 299))
    X = preprocessor.from_url(URI)
    return X


def np_to_protobuf(data):
    return tf.make_tensor_proto(data, shape=data.shape)

def show_image(URI):
    response = requests.get(URI)
    img = Image.open(BytesIO(response.content))
    img.show()
    return img

def predict(X):

    pb_request = predict_pb2.PredictRequest()
    pb_request.model_spec.name = 'clothing-model'
    pb_request.model_spec.signature_name = 'serving_default'
    pb_request.inputs['input_8'].CopyFrom(np_to_protobuf(X))
    pb_response = stub.Predict(pb_request, timeout=20.0)
    return pb_response.outputs['dense_7'].float_val

if __name__ == '__main__':

    URI = 'http://bit.ly/mlbookcamp-pants'
    show_image(URI)
    X = load_and_preprocess_data(URI)
    predictions = predict(X)
    print(dict(zip(CLASSES, predictions)))