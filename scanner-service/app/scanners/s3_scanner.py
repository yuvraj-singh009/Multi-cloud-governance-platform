from botocore.exceptions import ClientError

from app.config import get_aws_client


def scan_s3():

    s3 = get_aws_client("s3")

    response = s3.list_buckets()

    resources = []

    for bucket in response.get("Buckets", []):

        bucket_name = bucket["Name"]

        policy = None
        public_access_block = None

        try:
            result = s3.get_bucket_policy(
                Bucket=bucket_name
            )

            import json

            policy = json.loads(result["Policy"])

        except ClientError:
            policy = None

        try:
            result = s3.get_public_access_block(
                Bucket=bucket_name
            )

            public_access_block = result.get(
                "PublicAccessBlockConfiguration"
            )

        except ClientError:
            public_access_block = None

        resources.append({

            "resource_id": bucket_name,

            "resource_type": "S3",

            "resource_name": bucket_name,

            "region": "ap-south-1",

            "resource_state": "available",

            "configuration": {

                "bucket_name": bucket_name,

                "policy": policy,

                "public_access_block": public_access_block

            }

        })

    return resources