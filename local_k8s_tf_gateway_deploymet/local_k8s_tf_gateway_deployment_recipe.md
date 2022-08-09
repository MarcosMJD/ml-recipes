# Deploy a local kubernetes cluster with gateway and tensorflow server

Create a Kubernetes local cluster with Kind.  
Deploy tf serving and ml model into the cluster.  
Deploy a gateway that loads and preprocesses features into the cluster.  
Create Kubernetes services for each deployment.  

- [Deploy a local kubernetes cluster with gateway and tensorflow server](#deploy-a-local-kubernetes-cluster-with-gateway-and-tensorflow-server)
  - [Ingredients:](#ingredients)
  - [Setup](#setup)
  - [Install kubectl and kind](#install-kubectl-and-kind)
    - [Install kubectl](#install-kubectl)
    - [Install Kind](#install-kind)
  - [Create cluster](#create-cluster)
  - [Set kubectl to work with the cluster](#set-kubectl-to-work-with-the-cluster)
  - [Load Docker images into the cluster](#load-docker-images-into-the-cluster)
  - [Create and apply deployments and services](#create-and-apply-deployments-and-services)
  - [Test tf-service via port forwarding to the service.](#test-tf-service-via-port-forwarding-to-the-service)
  - [Test gateway and its connection with tf-serving](#test-gateway-and-its-connection-with-tf-serving)


## Ingredients:
  Kubectl
  kind
  Docker
  Docker image of gateway
  Docker image of tf serving
  Python test scripts
    Python: 3.9
      grpcio = "==1.42.0"
      tensorflow-serving-api = "==2.7.0"
      pillow = "*"
      tensorflow = "==2.9.1"
      keras-image-helper = "*"

## Setup

```bash
pip install -U pip
pip install pipenv 
pipenv install --dev
shell pipenv
```

## Install kubectl and kind

### Install kubectl
https://kubernetes.io/es/docs/tasks/tools/
In Windows, it should have been installed when installing Docker.

### Install Kind
https://kind.sigs.k8s.io/docs/user/quick-start/#installation
```bash
curl.exe -Lo kind-windows-amd64.exe https://kind.sigs.k8s.io/dl/v0.14.0/kind-windows-amd64
Move-Item .\kind-windows-amd64.exe kind.exe 
``` 

## Create cluster

```bash
kind create cluster --name tf-gateway
kubectl config view

apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: DATA+OMITTED
    server: https://127.0.0.1:61608
  name: kind-tf-gateway
contexts:
- context:
    cluster: kind-tf-gateway
    user: kind-tf-gateway
  name: kind-tf-gateway
current-context: kind-tf-gateway
kind: Config
preferences: {}
users:
- name: kind-tf-gateway
  user:
    client-certificate-data: REDACTED
    client-key-data: REDACTED
```
## Set kubectl to work with the cluster
```bash
kubectl cluster-info --context kind-tf-gateway
```

## Load Docker images into the cluster
```bash
kind load docker-image tf_serving:v1 gateway_tf_serving:v1 --name tf-gateway
```

## Create and apply deployments and services
Check these files:
- gateway-deployment.yaml
- gateway-service.yaml
- model-deployment.yaml
- model-service.yaml
```bash
kubectl apply -f model-deployment.yaml
kubectl apply -f model-service.yaml
kubectl apply -f gateway-deployment.yaml
kubectl apply -f gateway-service.yaml
```

## Test tf-service via port forwarding to the service. 
```bash
kubectl get service
kubectl port-forward service/tf-serving  8500:8500
python test_tf_serving.py
```
```
{'dress': -1.8798636198043823, 'hat': -4.756310939788818, 'longsleeve': -2.359532356262207, 'outwear': -1.0892645120620728, 'pants
-1.0892645120620728, 'pants': 9.90378189086914, 'shirt': -2.8261780738830566, 'shoes': -3.6483104228973812, 'skirt': -2.612095594439, 'shorts': 3.24115252494812, 'skirt': -2.612095594406128, 't-shirt': -4.852035045623779}
```

## Test gateway and its connection with tf-serving 
```bash
kubectl port-forward service/gateway 9000:80
```
Host port 9000 is forwarding to port 80 of the gateway service where it is listening to. Actually Port 80 of service forwards to port 9000 of container, where gunicorn is listening to.

Run test script in another terminal
```
python test-gateway.py
{'dress': -1.8798636198043823, 'hat': -4.756310939788818, 'longsleeve': -2.359532356262207, 'outwear': -1.0892645120620728, 'pants
-1.0892645120620728, 'pants': 9.90378189086914, 'shirt': -2.8261780738830566, 'shoes': -3.6483104228973812, 'skirt': -2.612095594439, 'shorts': 3.24115252494812, 'skirt': -2.612095594406128, 't-shirt': -4.852035045623779}
```

Ignore error "error copying from local connection to remote stream". It is related to the use of grpc


