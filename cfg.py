# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Application Configuration
# Note: changing the APP_NAME will result in a new stack being provisioned
APP_NAME = "mirth-connect-on-aws"
JDBC_CHANNEL_STACK_NAME="mirth-jdbc-channel-example"
APP_VERSION = "version 0.1"
CFN_STACK_DESCRIPTION = "MirthConnect on AWS (" + APP_VERSION + ")"
CFN_JDBC_CHANNEL_STACK_DESCRIPTION = "This stack deploys JDBC to S3 (CSV) channel on Mirth with sample patient data in RDS able"

DEPLOY_REGION="us-east-1"

# VPC options
VPC_CIDR = "10.23.0.0/16" # cidr for the vpc that will be provisioned.
PUBLIC_LOAD_BALANCER = False # If this is set to True, the NLB will have a public Internet IP address

NAME_PREFIX = "mirth"

# Fargate task defintion parameters
# https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html
REGISTRY_IMAGE = "nextgenhealthcare/connect:latest"
TASK_CPU=2048
TASK_MEMORY_MIB=4096
TASK_COUNT=1
AUTOSCALE_MAX_TASKS=1
# Enable below if ssh access to the containers is required (useful for debugging). 
TASK_ENABLE_EXEC_COMMAND=False

# DATABASE CONFIG
DEFAULT_DATABASE_NAME="mirthdb"
DEFAULT_DATABASE_ADMIN_USER="mirthdbadmin"
RDS_INSTANCE_TYPE="r6g.large"

# mirthconnect options
MIRTH_REPOSITORY="nextgenhealthcare/connect"
MIRTH_ADMIN_PORT=8443
DATABASE_PORT=5432

ALLOWED_ADMIN_PEERS = {
    # used for container port mapping and security groups
    VPC_CIDR, # access from the provisioned VPC 
    # specify additional allowed peers:
    #"172.31.0.0/16", # Allow from a subnet, in a peered VPC or remote private network.
    #"123.123.123.123/32", # Allow access from individual IP address, public or private
    #"0.0.0.0/0", # Allow access from anywhere
}

# NOTE 1: 
# Service ports below need to be up and responding to the NLB healthchecks. If not, the deployment will fail.
# If you don't know which ports you will be using for your channels yet, leave the section below empty for your initial deployment, 
# and then add the configuration below and re-deploy after channels are live and responding.
# NOTE 2:
#    NLBs have a limit of 50 listeners. If more ports are needed - additional NLBs can be provisioned.
ALLOWED_CHANNEL_PORTS_AND_PEERS = {
    # used for container port mapping and security groups
    #10001 : { VPC_CIDR, "172.31.0.0/16" , "10.10.10.0/24" }, # allow access to port 10001 from the VPC and two other subnets
    #10002 : { VPC_CIDR, "123.123.123.123/32" }, # allow access to port 10002 from the VPC and an individual IP address
    #10003 : {"0.0.0.0/0"}, # Allow access to port 10003 from anywhere
}
