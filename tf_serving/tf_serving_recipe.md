# Tensorflow serving recipe

Deploy an existing deep learning model for image classification of clothes with Tensorflow Serving in Docker

- [Tensorflow serving recipe](#tensorflow-serving-recipe)
  - [Ingredients](#ingredients)
  - [Create environment for testing](#create-environment-for-testing)
  - [Convert model](#convert-model)
  - [Build the image](#build-the-image)
  - [Run the image](#run-the-image)
  - [Make a prediction request to tensoflow serving](#make-a-prediction-request-to-tensoflow-serving)

## Ingredients

- Model: https://github.com/alexeygrigorev/mlbookcamp-code/releases/download/chapter7-model/xception_v4_large_08_0.894.h5
- Docker
- Tensorflow serving docker image
- Script to convert model format
- Script for testing
- Image for testing: http://bit.ly/mlbookcamp-pants
- Python 3.9.x
  - pipenv
  - grpcio = "==1.42.0"
  - tensorflow-serving-api = "==2.7.0"
  - pillow = "*"
  - tensorflow = "==2.9.1"
  - keras-image-helper = "*"

## Create environment for testing
```bash
pip install -U pip
pip install pipenv
pipenv install --dev
pipenv shell
```

## Convert model
```bash
python download_and_convert_model.py clothing-model.h5
```
Check with 
```bash
saved_model_cli show --dir clothing-model --all

signature_def['serving_default']:
  The given SavedModel SignatureDef contains the following input(s):
    inputs['input_8'] tensor_info:
        dtype: DT_FLOAT
        shape: (-1, 299, 299, 3)
        name: serving_default_input_8:0
  The given SavedModel SignatureDef contains the following output(s):
    outputs['dense_7'] tensor_info:
        dtype: DT_FLOAT
        shape: (-1, 10)
        name: StatefulPartitionedCall:0
  Method name is: tensorflow/serving/predict
```

## Build the image
```bash
docker build .
```

## Run the image
```bash
docker run -it --rm -p 8500:8500 tf_serving:v1
```

## Make a prediction request to tensoflow serving
This will show the input image and the prediction results (multiclass classiffication)
```
python test_tf_serving.py
```