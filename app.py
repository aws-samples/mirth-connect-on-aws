#!/usr/bin/env python3

import aws_cdk as cdk
import cfg
from stacks import MirthConnectStack

#Initializing the stack
app = cdk.App()
MirthConnectStack(app, cfg.APP_NAME, description=cfg.CFN_STACK_DESCRIPTION)
app.synth()