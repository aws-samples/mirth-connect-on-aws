# Application Configuration
# Note: changing the APP_NAME will result in a new stack being provisioned
APP_NAME = "MIRTH"
APP_VERSION = "version 0.1"
CFN_STACK_DESCRIPTION = "MirthConnect on AWS (" + APP_VERSION + ")"

# Network options

VPC_CIDR = "10.23.0.0/16"
# Configure load balancer to be Internet-facing. True/False. If set to False, access will only be possible from within the VPC.
PUBLIC_LOAD_BALANCER = True
# Allow list of non-VPC IPs that can access the services. By default only access from within the VPC is allowed.
ALLOWED_PEERS = {
    "0.0.0.0/0", # Allow access from anywhere
}

NAME_PREFIX = "mirth"

# Fargate task defintion parameters
# https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html
REGISTRY_IMAGE = "nextgenhealthcare/connect:latest"
TASK_CPU=4096
TASK_MEMORY_MIB=8192
TASK_COUNT=1
AUTOSCALE_MAX_TASKS=10
# enable exec command to allow ssh to each task for debugging
TASK_ENABLE_EXEC_COMMAND=True

#DATABASE CONFIG
DEFAULT_DATABASE_NAME="mirthdb"
DEFAULT_DATABASE_ADMIN_USER="admin"

# mirthconnect options
MIRTH_REPOSITORY="nextgenhealthcare/connect"
MIRTH_ADMIN_PORT=8443
MYSQL_PORT=3306
MIRTH_CHANNEL_PORT=10001

