import os
import boto3

from dotenv import load_dotenv

load_dotenv()


AWS_REGION = os.getenv(
    "AWS_DEFAULT_REGION",
    "ap-south-1"
)

AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL")


def get_aws_client(service_name: str):

    return boto3.client(
        service_name,
        region_name=AWS_REGION,
        endpoint_url=AWS_ENDPOINT_URL or None,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )