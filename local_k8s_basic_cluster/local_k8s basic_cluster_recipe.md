# Kubernetes recipe (fast & functional)

Create a kubernetes cluster and deploy a simple web service

- [Kubernetes recipe (fast & functional)](#kubernetes-recipe-fast--functional)
  - [Ingredients](#ingredients)
  - [Setup](#setup)
  - [Create simple app ping.py](#create-simple-app-pingpy)
  - [Create container](#create-container)
    - [Create Dockerfile](#create-dockerfile)
    - [Build container](#build-container)
  - [Create Local Kubernetes Cluster](#create-local-kubernetes-cluster)
    - [Install kubectl](#install-kubectl)
    - [Install Kind](#install-kind)
    - [Create Cluster with Kind](#create-cluster-with-kind)
      - [Setup kubectl to access new cluster](#setup-kubectl-to-access-new-cluster)
      - [Check cluster with kubectl](#check-cluster-with-kubectl)
      - [Load the image into the cluster](#load-the-image-into-the-cluster)
      - [Create a deployment](#create-a-deployment)
    - [Create a service](#create-a-service)

https://kubernetes.io/
https://www.docker.com/

## Ingredients

  - Docker
  - kubectl
  - kind
  - Python
    - Flask
    - Gunicorn

## Setup

```bash
pip install -U pip
pip install pipenv
pipenv install
shell pipenv
```

## Create simple app ping.py
```
from flask import Flask

app = Flask('ping')

@app.route('/ping', methods=['GET'])
def ping():
  return "PONG"

if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0', port=9000)
```

Test with 
```
curl http://localhost:9000/ping
```

## Create container

### Create Dockerfile

```
from python:3.9.5-slim

RUN pip install -U pip
RUN pip install pipenv

COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --system --deploy

COPY ["ping.py", "./"]

EXPOSE 9000

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:9000", "ping:app"]
```

### Build container
```
docker build -t ping:v1 .
```

Run container
```
docker run -it --rm -p 9000:9000 ping:v1
``` 
Test with 
```
curl http://localhost:9000/ping
```

## Create Local Kubernetes Cluster

### Install kubectl
https://kubernetes.io/es/docs/tasks/tools/
In Windows, it should have been installed when installing Docker.

### Install Kind
https://kind.sigs.k8s.io/docs/user/quick-start/#installation
```bash
curl.exe -Lo kind-windows-amd64.exe https://kind.sigs.k8s.io/dl/v0.14.0/kind-windows-amd64
Move-Item .\kind-windows-amd64.exe kind.exe
```
### Create Cluster with Kind
Kind runs a Docker container to deploy Kubernetes cluster locally. So that kubectl interacts with this cluster. Default cluster name is "kind". 
```bash 
kind create cluster
```
#### Setup kubectl to access new cluster
```
kubectl cluster-info --context kind-kind
```
#### Check cluster with kubectl 
```bash
kubectl get service

NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   6m20s
```
#### Load the image into the cluster
```bash
kind load docker-image ping:v1
```
#### Create a deployment
Create  deployment.yaml
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ping-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ping-pod
  template:
    metadata:
      labels:
        app: ping-pod
    spec:
      containers:
      - name: ping-container
        image: ping:v1
        resources:
          limits:
            memory: "128Mi"
            cpu: "500m"
        ports:
        - containerPort: 9000
```
Run 
```bash
kubectl apply -f deployment.yaml
```
Check with:
```bash
kubectl get deployment
kubectl get pod
kubectl describe pod <pod-id>
kubectl port-forward <pod-id> 9000:9000
curl http://localhost:9000/ping
```
Notes:  
https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#port-forward  
`kubectl port-forward TYPE/NAME [options] [LOCAL_PORT:]REMOTE_PORT [...[LOCAL_PORT_N:]REMOTE_PORT_N]`  
curl shall be run in another terminal

### Create a service
Create service.yaml
```
apiVersion: v1
kind: Service
metadata:
  name: ping
spec:
  type: LoadBalancer
  selector:
    app: ping-pod
  ports:
  - port: 80
    targetPort: 9000
```
Run 
```bash 
kubectl apply -f service.yaml
```
Check with:
```bash
kubectl get service

NAME         TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
kubernetes   ClusterIP      10.96.0.1      <none>        443/TCP          63m
ping         LoadBalancer   10.96.195.26   <pending>     8080:30146/TCP   2m32s

kubectl port-forward service/ping 8080:80

Forwarding from 127.0.0.1:8080 -> 9000
Forwarding from [::1]:8080 -> 9000

curl http://localhost:8080/ping
```

External ip is pending because we are in a local kubernetes cluster. Cloud services will assign the external ip.
So check with port-forwarding to the service. Local port will be 8080, remote will be 80. Actually the port forwarding will be to 9000
because the load balancer is what it does.



