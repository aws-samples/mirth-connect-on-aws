#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import aws_cdk as cdk
import cfg
from stacks.mirth_connect_on_aws import MirthConnectStack
from stacks.jdbc_to_csv_channel import JDBCtoCSVChannel

#Initializing the stack
app = cdk.App()
mirth_stack = MirthConnectStack(app, cfg.APP_NAME, description=cfg.CFN_STACK_DESCRIPTION)
jdbc_example_stack = JDBCtoCSVChannel(app, cfg.JDBC_CHANNEL_STACK_NAME, 
                                      description=cfg.CFN_JDBC_CHANNEL_STACK_DESCRIPTION,
                                      mirth_stack=mirth_stack)
app.synth()