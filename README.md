
# Mirth Connect on AWS

## Introduction
This repository contains sample application to build resilient and higly-available Mirth® Connect by NextGen Healthare on AWS. Mirth Connect interprets messages of any standard into the standard your target system understands. It has four capabilities such as:
1. Filering
2. Transformation
3. Extraction
4. Routing

## Prerequisites: ##
- AWS account
- Python3 and PIP


## Architecture

![Architecture - Fargate](images/mirthfargate_architecture.png)

The sample uses the AWS Cloud Development Kit (CDK) to automate deployment of resources. The stack leverages Amazon Elastic Container Services (ECS) deployed on AWS Fargate to run containers without having to manage servers. The following resources are provisioned:
1. Network Layer: VPC, Subnets, NLB, NAT Gateway, VPC Endpoints
2. Amazon ECS Cluster, Fargate Tasks
3. Amazon Aurora/RDS Postgres
4. Code*... [todo]

## Mirth Configuration

[todo]

## Cleanup
## Security
## License


## Deployment:

Infrastructure is provisioned using AWS CDK v2. The `cdk.json` file tells the CDK Toolkit how to execute your app. 

After cloning the repo code, the following steps can be used to set up the environment and deploy the application.

1. Create a Python virtualenv (this only needs to be done once):

```
$ python3 -m venv .mpenv
```

2. Activate the virtual environment:
```
$ source .mpenv/bin/activate
```

3. Install dependecies:
```
$ pip install -r requirements.txt
```

4. Synthesize the CloudFormation template for this code:
```
$ cdk synth
```

5. Deploy this stack to your default AWS account/region:
```
$ cdk deploy
```


## Useful CDK commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation