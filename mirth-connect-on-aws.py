#!/usr/bin/env python3

from constructs import Construct
from aws_cdk import (
	App,
	CfnOutput,
	Duration,
	Stack,
	RemovalPolicy,
	aws_ec2 as ec2,
	#aws_s3 as s3,
	#aws_ecr as ecr,
	aws_iam as iam,
	#aws_ecr_assets as ecrassets,
	aws_ecs as ecs,
	aws_ecs_patterns as ecs_patterns
)
import os

import cfg

class MirthConnectStack(Stack):

	def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
		super().__init__(scope, construct_id, **kwargs)
		
		region = self.region
		account = self.account
		
		# VPC
		vpc = ec2.Vpc(
			scope=self,
			id='VPC',
			max_azs=3,
			cidr=cfg.VPC_CIDR,
			subnet_configuration=[
				# modify here to change the types of subnets provisioned as part of the VPC
				ec2.SubnetConfiguration(
					subnet_type=ec2.SubnetType.PUBLIC, 
					name="Public", 
					cidr_mask=24
				),
				ec2.SubnetConfiguration(
					subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
					name="PrivateWithNat",
					cidr_mask=24,
				),
				#ec2.SubnetConfiguration(
				#	subnet_type=ec2.SubnetType.PRIVATE_ISOLATED, 
				#	name="PrivateIsolated",
				#	cidr_mask=24,
				#),
			],
			nat_gateway_provider=ec2.NatProvider.gateway(),
			nat_gateways=1,  # Only provision 1 NAT GW - default is one per one per AZ
		)

		# VPC Endpoint for S3 (Gateway)
		#s3gwendpoint = vpc.add_gateway_endpoint("S3-GW-EP",service=ec2.GatewayVpcEndpointAwsService.S3)
		#s3_gw_vpce = ec2.GatewayVpcEndpoint(
		#	scope=self, 
		#	id='s3GwVpce',
		#	service=ec2.GatewayVpcEndpointAwsService.S3,
		#	vpc=vpc,
		#	# limit which subnets will have routes to the endpoint:
		#	#subnets=[ec2.SubnetSelection(
		#	#    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
		#	#)]
		#)

		# VPC Endpoint for ECR API
		#ecr_api_if_vpce = vpc.vpc.add_interface_endpoint("EcrApiEndpoint",service=ec2.InterfaceVpcEndpointAwsService.ECR)
		#ecr_api_if_vpce = ec2.InterfaceVpcEndpoint(
		#	scope=self, 
		#	id='EcrIfVpce',
		#	service=ec2.InterfaceVpcEndpointAwsService.ECR,
		#	vpc=vpc,
		#	#private_dns_enabled=True,
		#	#security_groups=[security_group],
		#	#subnets=ec2.SubnetSelection(
		#	#    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
		#	#)
		#)

		# VPC Endpoint for ECR Docker
		#ecr_dkr_if_vpce = vpc.vpc.add_interface_endpoint("EcrDockerEndpoint",service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER)
		#ecr_dkr_if_vpce = ec2.InterfaceVpcEndpoint(
		#	scope=self, 
		#	id='EcrDkrIfVpce',
		#	service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
		#	vpc=vpc,
		#	#private_dns_enabled=True,
		#	#security_groups=[security_group],
		#	#subnets=ec2.SubnetSelection(
		#	#    subnet_type=ec2.SubnetType.PRIVATE
		#	#)
		#)

		# create ECS cluster
		cluster = ecs.Cluster(
			scope=self,
			id='ECSCluster',
			#
			vpc=vpc
		)
		
		# Build Docker asset
		#asset = ecrassets.DockerImageAsset(
		#	scope=self,
		#	id='DockerAsset',
		#	directory='container',
		#	build_args={
        #    	"MIRTH_ADMIN_PORT": str(cfg.MIRTH_ADMIN_PORT),
        #    	"MIRTH_CHANNEL_PORT": str(cfg.MIRTH_CHANNEL_PORT)
		#	}
		#)	
		
		# Fargate Task Properties
		# https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/ContainerImage.html
		task_image_props=ecs_patterns.NetworkLoadBalancedTaskImageProps(
			image=ecs.ContainerImage.from_registry(cfg.REGISTRY_IMAGE),
			container_name="mirthconnect",
			container_ports=[
				cfg.MIRTH_ADMIN_PORT,
				cfg.MIRTH_CHANNEL_PORT
			],
			environment={
            	"MIRTH_ADMIN_PORT": str(cfg.MIRTH_ADMIN_PORT),
            	"MIRTH_CHANNEL_PORT": str(cfg.MIRTH_CHANNEL_PORT)
        	}
		)

		# Fargate Service
		fargate_service = ecs_patterns.NetworkMultipleTargetGroupsFargateService(
			scope=self,
			id='FG',
			cluster=cluster,
			cpu=cfg.TASK_CPU,
			memory_limit_mib=cfg.TASK_MEMORY_MIB,
			desired_count=cfg.TASK_COUNT,
			task_image_options=task_image_props,
			# enable below to be able to exec ssh to the Fargate container
			enable_execute_command=cfg.TASK_ENABLE_EXEC_COMMAND,
			load_balancers=[ecs_patterns.NetworkLoadBalancerProps(
        		name="NLB",
        		public_load_balancer=cfg.PUBLIC_LOAD_BALANCER,
        		listeners=[
        			ecs_patterns.NetworkListenerProps(name="mirthadmin",port=cfg.MIRTH_ADMIN_PORT)
        		]
    			)
    		],
    		target_groups=[
    			ecs_patterns.NetworkTargetProps(listener="mirthadmin",container_port=cfg.MIRTH_ADMIN_PORT)
    		]
		)

		# Set max tasks value for Autoscaling
		fargate_scaling_group = fargate_service.service.auto_scale_task_count(
			max_capacity=cfg.AUTOSCALE_MAX_TASKS
		)
		
		# Autoscaling policy for the fargate service - CPU utilization
		#fargate_scaling_group.scale_on_cpu_utilization(
		#	"CpuScaling",
		#	target_utilization_percent=50,
		#	scale_in_cooldown=Duration.seconds(60),
		#	scale_out_cooldown=Duration.seconds(60),
		#)
		
		# Autoscaling policy for the fargate service - # of Connections through NLB
		#fargate_scaling.scale_on_metric(
        #    "CpuScaling",
        #    target_utilization_percent=50,
        #    scale_in_cooldown=Duration.seconds(60),
        #    scale_out_cooldown=Duration.seconds(60),
        #)

		# Enable client IP preservation on the LB target groups (needed for Allow List inspection)
		for target_group in fargate_service.target_groups:
			target_group.set_attribute('preserve_client_ip.enabled','true')
		
		# S3 access policy statement for the task role
		#policy_statement = iam.PolicyStatement(
		#	effect = iam.Effect.ALLOW,
		#	actions = [
		#			's3:ListBucket',
		#			's3:PutObject'
		#		],
		#		resources = [
		#			receive_bucket.bucket_arn, 
		#			f"{receive_bucket.bucket_arn}/*"
		#		]
		#)
		# Grant S3 bucket access to the Fargate task role
		#fargate_service.task_definition.task_role.add_to_principal_policy(policy_statement)
		
		port_list = [cfg.MIRTH_ADMIN_PORT]
		
		# Security Group rules
		for port in port_list :
			# VPC access
			fargate_service.service.connections.security_groups[0].add_ingress_rule(
           		peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
           		connection = ec2.Port.tcp(port),
           		description="Allow from VPC"
        	)
        	# Allow Peer access
			for cidr in cfg.ALLOWED_PEERS :
				fargate_service.service.connections.security_groups[0].add_ingress_rule(
            		peer = ec2.Peer.ipv4(cidr),
            		connection = ec2.Port.tcp(port),
            		description="Allow from " + cidr
        		)


		# Output the DNS of the LoadBalancer
		#CfnOutput(
        #    self, "LoadBalancerDNS",
        #    value=fargate_service.load_balancer.load_balancer_dns_name
        #)


app = App()

MirthConnectStack(app, cfg.APP_NAME, description=cfg.CFN_STACK_DESCRIPTION
	# If you don't specify 'env', this stack will be environment-agnostic.
	# Account/Region-dependent features and context lookups will not work,
	# but a single synthesized template can be deployed anywhere.

	# Uncomment the next line to specialize this stack for the AWS Account
	# and Region that are implied by the current CLI configuration.

	#env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

	# Uncomment the next line if you know exactly what Account and Region you
	# want to deploy the stack to. */

	#env=cdk.Environment(account='123456789012', region='us-east-1'),

	# For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
	)
app.synth()
