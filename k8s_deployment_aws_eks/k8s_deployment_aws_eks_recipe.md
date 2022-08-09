# Deployment a Kubernetes cluster in AWS EKS

Setup AWS CLI and eksctl tools
Create EKS cluster with eksctl
Create ECR repo
Upload Docker images to ECR repo
Apply deployments and services
Check with test script requesting to cluster endpoint (load balancer) 

- [Deployment a Kubernetes cluster in AWS EKS](#deployment-a-kubernetes-cluster-in-aws-eks)
  - [Ingredients](#ingredients)
  - [Setup](#setup)
  - [Download eksctl](#download-eksctl)
  - [Create EKS cluster](#create-eks-cluster)
    - [Check eks-config file](#check-eks-config-file)
    - [Create cluster](#create-cluster)
  - [Upload local Docker images to AWS ECR](#upload-local-docker-images-to-aws-ecr)
    - [Create new repository in ECR](#create-new-repository-in-ecr)
    - [Tag local images to remote repository](#tag-local-images-to-remote-repository)
    - [Authenticate in ECR](#authenticate-in-ecr)
    - [Push images to ECR repository](#push-images-to-ecr-repository)
  - [Create and apply deployments and services](#create-and-apply-deployments-and-services)
    - [Check gateway with port forwarding](#check-gateway-with-port-forwarding)
    - [Get external url of gateway service and test](#get-external-url-of-gateway-service-and-test)
  - [Delete cluster](#delete-cluster)
  - [ToDo](#todo)


## Ingredients

- AWS account
  - EKS Elastic Kubernetes Service (uses EC2 and EC2 Load Balancer feature)
  - ECR Elastic Container Registry
- AWS CLI tool
- eksctl tool
- Docker image with gateway
- Docker image with tensorflow serving and model

## Setup

Create AWS credentials files under C:\Users\<USERNAME>\.aws\
- config
- credentials

These files can by generated with AWS CLI tool by running `aws configure` 
https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

## Download eksctl
https://docs.aws.amazon.com/eks/latest/userguide/eksctl.html  
https://github.com/weaveworks/eksctl/releases/download/v0.103.0/eksctl_Windows_amd64.zip  

## Create EKS cluster

### Check eks-config file

```
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: tf-gateway-eks
  region: eu-west-1

nodeGroups:
  - name: ng-m5-xlarge
    instanceType: m5.xlarge
    desiredCapacity: 1
```
There is no need to use an EC2 type with GPU. For testing, only 1 node instance is used.  
Node groups may be used to group nodes by instance type. For instance, one group with GPU and one without.  
Deployments may be assigned to nodes by using tags (not used in this example).  

### Create cluster
```bash
eksctl create cluster -f eks-config.yaml
```
After that, kubectl is already set to use the eks cluster.  
Check with:  
```bash
kubectl config view
kubectl get nodes
```

## Upload local Docker images to AWS ECR

### Create new repository in ECR
`aws ecr create repository --repository-name tf-gateway`  
Write down the repository url. E.g.:
`546106488772.dkr.ecr.eu-west-1.amazonaws.com/tf-gateway`

### Tag local images to remote repository
Note that if we push both images to the same repository, we need to set remote tags in such a way that distinguish between tf-server and gateway images.
```
docker tag tf_serving:v1 546106488772.dkr.ecr.eu-west-1.amazonaws.com/tf-gateway:tf_serving-v1
docker tag gateway_tf_serving:v1 546106488772.dkr.ecr.eu-west-1.amazonaws.com/tf-gateway:gateway_tf_serving-v1
```
### Authenticate in ECR
```bash
aws ecr get-login-password `
    --region <region> `
| docker login `
    --username AWS `
    --password-stdin <aws_account_id>.dkr.ecr.eu-west-1.amazonaws.com
```
In Linux, change ` with \
Region example: eu-west-1

### Push images to ECR repository
docker push 546106488772.dkr.ecr.eu-west-1.amazonaws.com/tf-gateway:tf_serving-v1
docker push 546106488772.dkr.ecr.eu-west-1.amazonaws.com/tf-gateway:gateway_tf_serving-v1

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

### Check gateway with port forwarding

`kubectl port-forward service/gateway 9000:80` 
Test in another terminal with:
`python test_gateway.py`

### Get external url of gateway service and test

`kubectl get service`
`http://aa792658e2058482eb6b1a6c855d15a7-245429963.eu-west-1.elb.amazonaws.com:80` 
Note: Take some minutes for DNS propagation
Note: This url is the DNS name of the load balancer that EKS launches when deploying the service type load balancer.

Test with:
`python .\test_gateway.py http://aa792658e2058482eb6b1a6c855d15a7-245429963.eu-west-1.elb.amazonaws.com/predict`

## Delete cluster
eksctl delete cluster --name tf-gateway-eks

## ToDo
Set access policy to the load balancer (not open to everyone)