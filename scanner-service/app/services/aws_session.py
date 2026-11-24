
import boto3
import os

from app.config import (
    AWS_PROFILE,
    AWS_REGION,
    AWS_ENDPOINT_URL,
    AWS_CONNECTION_MODE
)


def get_aws_session():

    if AWS_CONNECTION_MODE == "local":
        session = boto3.Session(
            profile_name=AWS_PROFILE,
            region_name=AWS_REGION
        )

    elif AWS_CONNECTION_MODE == "container":
        # Uses the container's IAM role or
        # another configured AWS credential provider.
        session = boto3.Session(
            region_name=AWS_REGION
        )

    else:
        raise ValueError(
            "Unsupported AWS connection mode"
        )

    return session


def get_aws_client(service_name, region=None):

    session = get_aws_session()

    kwargs = {
        "region_name": region or AWS_REGION
    }

    if (
        AWS_CONNECTION_MODE == "local"
        and AWS_ENDPOINT_URL
    ):
        kwargs["endpoint_url"] = AWS_ENDPOINT_URL

    return session.client(
        service_name,
        **kwargs
    )

def get_aws_account_details():

    sts = get_aws_client("sts")

    identity = sts.get_caller_identity()

    return {
        "account_id": identity["Account"],
        "user_arn": identity["Arn"],
        "user_id": identity["UserId"]
    }