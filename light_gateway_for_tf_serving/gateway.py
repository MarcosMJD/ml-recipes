import grpc
from keras_image_helper import create_preprocessor
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
from flask import Flask, request, jsonify
from proto import np_to_protobuf
import os


ML_SERVER_HOST = os.getenv('TF_SERVING_HOST','localhost:8500')

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

channel = grpc.insecure_channel(ML_SERVER_HOST)
stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)


def load_and_preprocess_data(url):
    preprocessor = create_preprocessor('xception', target_size=(299, 299))
    X = preprocessor.from_url(url)
    return X



def prepare_request(X):

    pb_request = predict_pb2.PredictRequest()
    pb_request.model_spec.name = 'clothing-model'
    pb_request.model_spec.signature_name = 'serving_default'
    pb_request.inputs['input_8'].CopyFrom(np_to_protobuf(X))
    return pb_request


def prepare_response(pb_response):
    return dict(zip(CLASSES, pb_response.outputs['dense_7'].float_val))


def predict(url):

    X = load_and_preprocess_data(url)
    pb_request = prepare_request(X)
    pb_response = stub.Predict(pb_request, timeout=20.0)
    response = prepare_response(pb_response)
    return response

app = Flask('gateway')

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    data = request.get_json()
    url = data['url']
    result = predict(url)
    return jsonify(result)


if __name__ == '__main__':
    # url = 'http://bit.ly/mlbookcamp-pants'
    # response = predict(url)
    # print(response)
    app.run(debug=True, host='0.0.0.0', port=9000)
