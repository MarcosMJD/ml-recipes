import requests
import sys

URL = 'http://bit.ly/mlbookcamp-pants'

if __name__ == '__main__':

    GATEWAY = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:9000/predict'
    payload = {
      'url': URL
    }
    result = requests.post(GATEWAY, json=payload).json()
