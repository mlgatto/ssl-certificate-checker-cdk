from aws_cdk import (
    Tags,
    aws_events as events,
    aws_lambda as lambda_,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as actions,
    aws_events_targets as targets,
    App, Duration, Stack
)


"""
Defines the content of the CDK stack.
"""
class SslCheckerLambdaStack(Stack):
    def __init__(self, app: App, id: str) -> None:
        super().__init__(app, id)

        stage = app.node.try_get_context("stage") or "dev"
        settings = app.node.try_get_context(stage)

        with open("handler.py", encoding="utf8") as fp:
            handler_code = fp.read()

        lambda_fn = lambda_.Function(
            self, "Lambda",
            code=lambda_.InlineCode(handler_code),
            handler="index.main",
            timeout=Duration.seconds(300),
            runtime=lambda_.Runtime.PYTHON_3_9,
            environment={ "DOMAINS": ",".join(settings["domains"]) }
        )

        rule = events.Rule(
            self, "Rule",
            schedule=events.Schedule.rate(
                duration=Duration.minutes(30)
            )
        )
        rule.add_target(targets.LambdaFunction(lambda_fn))

        topic = sns.Topic(self, 'AlarmSns')
        topic.add_subscription(subscriptions.EmailSubscription(settings["email"]))

        alarm = cloudwatch.Alarm(
            self, 'LambdaErrorsAlarm',
            metric=lambda_fn.metric_errors(period=Duration.minutes(30)),
            threshold=1,
            evaluation_periods=1,
            actions_enabled=bool(settings["enableAlerts"])
        )

        alarm.add_alarm_action(actions.SnsAction(topic))
        alarm.add_ok_action(actions.SnsAction(topic))

app = App()
stack = SslCheckerLambdaStack(app, "SslCheckerLambda")
Tags.of(stack).add("team", "xops-dev")
app.synth()