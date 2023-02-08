#!/usr/bin/env python3

from constructs import Construct
from aws_cdk import (
	App,
	CfnOutput,
	Stack,
	aws_ec2 as ec2,
	aws_ecs as ecs,
	aws_rds as rds,
	aws_ecs_patterns as ecs_patterns
)
import cfg

class MirthConnectStack(Stack):

	def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
		super().__init__(scope, construct_id, **kwargs)
		
		# Creating a VPC for Mirth connect app to deploy
		vpc = ec2.Vpc(
			scope=self,
			id=cfg.NAME_PREFIX+'-vpc',
			max_azs=3,
			cidr=cfg.VPC_CIDR,
			subnet_configuration=[
				# modify here to change the types of subnets provisioned as part of the VPC
				ec2.SubnetConfiguration(
					subnet_type=ec2.SubnetType.PUBLIC, 
					name=cfg.NAME_PREFIX + "-Public", 
					cidr_mask=24
				),
				ec2.SubnetConfiguration(
					subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
					name= cfg.NAME_PREFIX + "-PrivateWithNat",
					cidr_mask=24,
				),
			],
			nat_gateway_provider=ec2.NatProvider.gateway(),
			nat_gateways=1,  # Only provision 1 NAT GW - default is one per one per AZ
		)
  
  		# print the arn for this VPC
		CfnOutput(self, "VPC", value=vpc.vpc_arn)

		dbcluster = rds.DatabaseCluster(self, "mirth-source-database",
			engine=rds.DatabaseClusterEngine.aurora_mysql(version=rds.AuroraMysqlEngineVersion.VER_2_10_2),
			credentials=rds.Credentials.from_generated_secret(cfg.DEFAULT_DATABASE_ADMIN_USER),  # Optional - will default to 'admin' username and generated password
			default_database_name= cfg.DEFAULT_DATABASE_NAME,
			instance_props=rds.InstanceProps(
				# optional , defaults to t3.medium
				instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.SMALL),
				vpc_subnets=ec2.SubnetSelection(
					subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
				),
				vpc=vpc
			)
		)
  
  		# print the db cluster identifier
		CfnOutput(self, "DBCluster", value=dbcluster.cluster_identifier)
		CfnOutput(self, "DBEndpoint", value=dbcluster.cluster_endpoint.hostname)
		
		# create ECS cluster
		cluster = ecs.Cluster(
			scope=self,
			id= cfg.NAME_PREFIX + '-ecs-cluster',
			vpc=vpc
		)
		
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
            	"MIRTH_CHANNEL_PORT": str(cfg.MIRTH_CHANNEL_PORT),
				"DATABASE": str('mysql'),
				"DATABASE_URL": str(f'jdbc:mysql://{dbcluster.cluster_endpoint.hostname}:{dbcluster.cluster_endpoint.port}/{cfg.DEFAULT_DATABASE_NAME}?enabledTLSProtocols=TLSv1.2'),
				"DATABASE_USERNAME": str(cfg.DEFAULT_DATABASE_ADMIN_USER),
				"DATABASE_PASSWORD": str(dbcluster.secret.secret_value_from_json('password').unsafe_unwrap()),
				"DATABASE_MAX_RETRY": str(2),
				"DATABASE_RETRY_WAIT": str(10000)
        	}
		)

		# Fargate Service
		fargate_service = ecs_patterns.NetworkMultipleTargetGroupsFargateService(
			scope=self,
			id= cfg.NAME_PREFIX + '-fargate',
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
		
		# Enable client IP preservation on the LB target groups (needed for Allow List inspection)
		for target_group in fargate_service.target_groups:
			target_group.set_attribute('preserve_client_ip.enabled','true')
		
		port_list = [cfg.MIRTH_ADMIN_PORT, cfg.MYSQL_PORT]
		
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
       			#Excluding database port to have access public cidr
				if(port == cfg.MYSQL_PORT): 
					continue
				fargate_service.service.connections.security_groups[0].add_ingress_rule(
            		peer = ec2.Peer.ipv4(cidr),
            		connection = ec2.Port.tcp(port),
            		description="Allow from " + cidr
        		)

		dbcluster.connections.allow_default_port_from(fargate_service.service.connections)

#Initializing the stack
app = App()
MirthConnectStack(app, cfg.APP_NAME, description=cfg.CFN_STACK_DESCRIPTION)
app.synth()