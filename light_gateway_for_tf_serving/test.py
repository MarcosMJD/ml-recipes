import requests

URL = 'http://bit.ly/mlbookcamp-pants'
GATEWAY = 'http://localhost:9000/predict'

if __name__ == '__main__':
    payload = {
      'url': URL
    }
    result = requests.post(GATEWAY, json=payload).json()
    print(result)