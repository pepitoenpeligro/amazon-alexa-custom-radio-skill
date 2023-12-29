#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infrastructure.amazon_alexa_custom_radio_skill_aws_stack import (
    AmazonAlexaCustomRadioSkillAWSStack,
)


app = cdk.App()
AmazonAlexaCustomRadioSkillAWSStack(
    scope=app,
    construct_id="amazon-alexa-construct",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)

app.synth()
