#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import aws_cdk as cdk
import cfg
from stacks.mirth_connect_on_aws import MirthConnectStack

#Initializing the stack
app = cdk.App()
mirth_stack = MirthConnectStack(app, cfg.APP_NAME, description=cfg.CFN_STACK_DESCRIPTION)
app.synth()