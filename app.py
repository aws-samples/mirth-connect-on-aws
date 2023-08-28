#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import aws_cdk as cdk
import cfg
from stacks.mirth_connect_on_aws import MirthConnectStack

#Initializing the stack
app = cdk.App()
mirth_stack = MirthConnectStack(
    app, 
    cfg.APP_NAME, 
    description=cfg.CFN_STACK_DESCRIPTION,
    env={'region':cfg.DEPLOY_REGION}
    )
# ensure CFT format version is listed in the output
mirth_stack.template_options.template_format_version = '2010-09-09'
app.synth()
