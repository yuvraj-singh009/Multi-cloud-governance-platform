import json
from botocore.exceptions import ClientError


def scan_s3(session):
    s3 = session.client("s3")
    resources = []
    response = s3.list_buckets()
    for bucket in response.get("Buckets", []):
        name = bucket["Name"]
        location = s3.get_bucket_location(Bucket=name).get("LocationConstraint") or "us-east-1"
        if location == "EU":
            location = "eu-west-1"
        policy = None
        policy_status = None
        public_access_block = None
        acl = None
        try:
            policy = json.loads(s3.get_bucket_policy(Bucket=name)["Policy"])
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") not in ("NoSuchBucketPolicy", "AccessDenied"):
                raise
        try:
            policy_status = s3.get_bucket_policy_status(Bucket=name).get("PolicyStatus", {})
        except ClientError:
            pass
        try:
            public_access_block = s3.get_public_access_block(Bucket=name).get("PublicAccessBlockConfiguration")
        except ClientError:
            pass
        try:
            acl = s3.get_bucket_acl(Bucket=name).get("Grants", [])
        except ClientError:
            pass
        resources.append({
            "resource_id": name, "resource_type": "S3", "resource_name": name,
            "region": location, "resource_state": "available",
            "configuration": {
                "bucket_name": name, "policy": policy, "policy_status": policy_status,
                "public_access_block": public_access_block, "acl": acl
            }
        })
    return resources
