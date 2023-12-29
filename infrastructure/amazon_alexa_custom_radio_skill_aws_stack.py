import aws_cdk
from constructs import Construct


class AmazonAlexaCustomRadioSkillAWSStack(aws_cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.function_lambda = aws_cdk.aws_lambda.Function(
            scope=self,
            id="alexa-skill",
            architecture=aws_cdk.aws_lambda.Architecture.ARM_64,
            function_name="amazon-alexa-custom-radio-skill-aws-stack",
            runtime=aws_cdk.aws_lambda.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            memory_size=128,
            timeout=aws_cdk.Duration.seconds(10),
            log_retention=aws_cdk.aws_logs.RetentionDays.TWO_MONTHS,
            runtime_management_mode=aws_cdk.aws_lambda.RuntimeManagementMode.AUTO,
            dead_letter_queue_enabled=False,
            retry_attempts=0,
            reserved_concurrent_executions=1,
            environment={
                "RADIO_STREAM_URL" : "https://srv7021.dns-lcinternet.com/8060/stream"
            },
            layers=[
                aws_cdk.aws_lambda.LayerVersion.from_layer_version_arn(
                    scope=self,
                    layer_version_arn="arn:aws:lambda:eu-west-1:580247275435:layer:LambdaInsightsExtension-Arm64:5",
                    id="lambda-insghts-layer",
                )
            ],
            code=aws_cdk.aws_lambda.Code.from_asset(
                "_code",
                bundling=aws_cdk.BundlingOptions(
                    image=aws_cdk.DockerImage.from_registry(
                        "public.ecr.aws/sam/build-python3.12"
                    ),
                    command=[
                        "bash",
                        "-c",
                        "pip install --no-cache -r requirements.txt -t /asset-output && rsync -r . /asset-output && LAMBDA_SIZE=$(du -sh /asset-output | awk '{print $1}')  && echo 'Lambda Code Asset Size: ' ${LAMBDA_SIZE}",
                    ],
                    platform="linux/arm64",
                    network="host",
                    security_opt="no-new-privileges:true",
                ),
            ),
        )

        self.function_lambda.role.add_managed_policy(
            aws_cdk.aws_iam.ManagedPolicy.from_managed_policy_arn(
                scope=self,
                id="managed",
                managed_policy_arn="arn:aws:iam::aws:policy/CloudWatchLambdaInsightsExecutionRolePolicy"
            )
        )
