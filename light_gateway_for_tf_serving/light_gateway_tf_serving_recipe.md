# Light gateway for Tensorflow Serving

Create a gateway that loads and preprocess features for a tensorflow model.  
Deploy the gateway in a docker container.  
Deploy an existing Docker image with tf serving and the model.  
Run and connect gateway with tf serving with a Docker network and make inferences.  
Run and connect gateway with tf serving with docker compose, and make inferences.  

- [Light gateway for Tensorflow Serving](#light-gateway-for-tensorflow-serving)
  - [Ingredients](#ingredients)
  - [Setup](#setup)
  - [Run de ml server image exposing port 8500 to the host](#run-de-ml-server-image-exposing-port-8500-to-the-host)
  - [Start web service](#start-web-service)
  - [Test gateway](#test-gateway)
  - [Build the Docker image](#build-the-docker-image)
  - [Run de ml server image in custom network](#run-de-ml-server-image-in-custom-network)
  - [Run the image in the same network as the server](#run-the-image-in-the-same-network-as-the-server)
  - [Check Docker composer yaml file to run the containers instead of running them manually](#check-docker-composer-yaml-file-to-run-the-containers-instead-of-running-them-manually)
  - [Test again](#test-again)


## Ingredients

  - Docker
  - Tensorflow server image containing the model as well
  - Gateway script
  - Test script
  - Python 3.9:
    - Flask
    - grpcio = "==1.42.0"
    - tensorflow-serving-api = "==2.7.0"
    - tensorflow-protobuf = "==2.7.0"
    - keras-image-helper = "*"
    - flask = "*"
    - gunicorn = "*"

## Setup
```bash
pip install -U pip
pip install pipenv
pipenv install
shell pipenv
```

## Run de ml server image exposing port 8500 to the host
```bash
docker run -it --rm -p 8500:8500  --name tf_serving tf_serving:v1 
```

## Start web service
```bash
python gateway.py
```
Note: default url of tf serving host will be used: localhost:8500

## Test gateway
```bash
python test.py
```

## Build the Docker image
```bash
 docker build -t gateway_tf_serving:v1 .
```

## Run de ml server image in custom network
Stop the running server container (CTRL+C)
```bash
docker network create ml
docker run -it --rm  --network ml -p --name tf_serving tf_serving:v1
```
Note: No need to expose port 8500 since both conatiners will be in the same network.
Only needed to expose if port 8500 of the server must be accessed by the host (i.e. execute some sort of test directly on the server)

## Run the image in the same network as the server
We need to set TF_SERVING_HOST to target the name of the container running the tensorflow server, since both containers are in the same network
```
docker run -it --rm --network ml -p 9000:9000 --name gateway --env TF_SERVING_HOST=tf_serving:8500 gateway_tf_serving:v1 
```
Test with:
```bash
python test.py
```

## Check Docker composer yaml file to run the containers instead of running them manually
Stop running containers (CTRL+C)
```
version: "3.9"
services:
  tf-serving:
    image: tf_serving:v1
    ports:
      - "8500:8500"
    
  gateway:
    image: gateway_tf_serving:v1
    environment:
      - TF_SERVING_HOST=tf-serving:8500
    ports:
      - "9000:9000"
```
```
docker-compose up
```

## Test again
```bash
python test.py
docker-compose down
```
