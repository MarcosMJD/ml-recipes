import tensorflow as tf
from tensorflow import keras
import sys
import requests

URL = 'https://github.com/alexeygrigorev/mlbookcamp-code/releases/download/chapter7-model/xception_v4_large_08_0.894.h5'


def download_model(url, local_filename = 'model'):

    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return local_filename


def convert_model(model_name):
    model = keras.models.load_model(model_name)
    model_name = model_name.partition(".")[0]
    tf.saved_model.save(model, model_name)

if __name__ == '__main__':

    model_name = sys.argv[1] if len(sys.argv) > 1 else URL.split('/')[-1]
    download_model(URL, model_name)
    convert_model(model_name)
  