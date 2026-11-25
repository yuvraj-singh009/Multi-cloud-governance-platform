"""AWS sessions for local development and cross-account customer roles."""
import re
import boto3
from botocore.config import Config
from app.config import AWS_PROFILE, AWS_REGION, AWS_ENDPOINT_URL, AWS_CONNECTION_MODE

ROLE_ARN_RE = re.compile(r"^arn:aws:iam::(?P<account>\d{12}):role/(?P<role>[A-Za-z0-9+=,.@_/-]{1,512})$")

def get_aws_session():
    mode = AWS_CONNECTION_MODE.lower()
    if mode == "local":
        return boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
    if mode == "container":
        return boto3.Session(region_name=AWS_REGION)
    raise ValueError("AWS_CONNECTION_MODE must be 'local' or 'container'")

def assume_customer_role(role_arn: str, external_id: str, region: str | None = None):
    if not ROLE_ARN_RE.fullmatch(role_arn or ""):
        raise ValueError("Invalid AWS IAM Role ARN")
    if not external_id or len(external_id) < 32:
        raise ValueError("Invalid External ID")
    platform = boto3.Session(region_name=region or AWS_REGION)
    sts = platform.client("sts", region_name=region or AWS_REGION,
                          config=Config(retries={"max_attempts": 4, "mode": "standard"}))
    credentials = sts.assume_role(RoleArn=role_arn, RoleSessionName="CloudGovernanceScan",
                                  ExternalId=external_id, DurationSeconds=3600)["Credentials"]
    return boto3.Session(aws_access_key_id=credentials["AccessKeyId"],
                         aws_secret_access_key=credentials["SecretAccessKey"],
                         aws_session_token=credentials["SessionToken"],
                         region_name=region or AWS_REGION)

def verify_customer_role(role_arn: str, external_id: str, expected_account_id: str):
    session = assume_customer_role(role_arn, external_id)
    identity = session.client("sts").get_caller_identity()
    if identity.get("Account") != expected_account_id:
        raise ValueError("Connected AWS role belongs to a different AWS account")
    return {"account_id": identity["Account"], "role_arn": identity["Arn"], "user_id": identity["UserId"]}

def get_customer_client(session, service_name: str, region: str | None = None):
    kwargs = {"region_name": region or AWS_REGION}
    if AWS_CONNECTION_MODE.lower() == "local" and AWS_ENDPOINT_URL:
        kwargs["endpoint_url"] = AWS_ENDPOINT_URL
    return session.client(service_name, **kwargs)

def get_aws_client(service_name, region=None):
    """Legacy local scanner client. Do not use for multi-tenant customer scans."""
    return get_customer_client(get_aws_session(), service_name, region)

def get_aws_account_details():
    identity = get_aws_client("sts").get_caller_identity()
    return {"account_id": identity["Account"], "user_arn": identity["Arn"], "user_id": identity["UserId"]}
