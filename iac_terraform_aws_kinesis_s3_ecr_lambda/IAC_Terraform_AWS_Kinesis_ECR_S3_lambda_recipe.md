# IAC setup of ML stream with Terraform on AWS Kinesis, ECR, S3 and Lambda

Ingredients:

AWS Kinesis - Event stream producer and consumer
AWS lambda container - Containerized Lambda function and model to run event based predictions
AWD ECR Container registry - for the container
S3 bucket - for model registry (there is no artifact server o model registry server)

- Requirements
  - AWS account
  - AWS access key (id and secret)
  - AWS cli: Download and install AWS cli
    - https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html  
    - Windows
      ```
      msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
      aws --version
      aws-cli/2.4.24 Python/3.8.8 Windows/10 exe/AMD64 prompt/off
      ```
  - Terraform
    - Download Terraform executable: https://www.terraform.io/downloads
    - Save it to ./infrastructure directory

Setup
   
  - AWS cli
      ````bash
      aws configure
      AWS Access Key ID [None]: [your aws key id]
      AWS Secret Access Key [None]: [your asw secret access key]
      Default region name [None]: eu-west-1
      Default output format [None]:
      aws sts get-caller-identity
      ```
  - Create terraform backend bucket to keep Terraform state
    Note: bucket names shall be unique. Choose your location accordingly.
    Note: bucket is private, objects  but anyone with appropriate permissions can grant public access to objects.
    ```bash
    aws s3api create-bucket --bucket [your bucket name] --create-bucket-configuration LocationConstraint=eu-west-1
    ```

  - Initialize Terraform
    - Run `terraform init` under ./infrastructure directory

