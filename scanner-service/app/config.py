import os
from dotenv import load_dotenv


import boto3

def get_aws_client(service_name: str, region_name: str = None):
    return boto3.client(service_name, region_name=region_name)


load_dotenv()

AWS_REGION = os.getenv(
    "AWS_REGION",
    "ap-south-1"
)

AWS_PROFILE = os.getenv(
    "AWS_PROFILE",
    "finops-dev"
)

AWS_ENDPOINT_URL = os.getenv(
    "AWS_ENDPOINT_URL"
)

AWS_CONNECTION_MODE = os.getenv(
    "AWS_CONNECTION_MODE",
    "local"
)