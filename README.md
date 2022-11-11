# Mirth Connect on AWS

## Introduction
This repository contains sample application to build resilient and higly-available Mirth® Connect by NextGen Healthare on AWS. Mirth Connect interprets messages of any standard into the standard your target system understands. It has four capabilities such as,
1. Filering
2. Transformation
3. Extraction
4. Routing


## Architecture

[Embed Archiecture Diagram]

The sample use AWS Cloud Development Kit (CDK) to automate deployment of resources. The stack leverages Amazon Elastic Container Services (ECS) deployed on AWS Fargate to run containers without having to manage servers. It also has following resources.
1. Network Layer: VPC, Subnets, and AZ
2. ECR, ECS Fargate Cluster
3. Amazon Aurora/RDS Postgres

## Mirth Configuration

## Steps to deploy

The `cdk.json` file tells the CDK Toolkit how to execute your app.

## Useful commands
* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk synth`       emits the synthesized CloudFormation template

## Cleanup
## Security
## License
