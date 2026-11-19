from app.config import get_aws_client


def scan_security_groups():

    ec2 = get_aws_client("ec2")

    response = ec2.describe_security_groups()

    resources = []

    for group in response.get("SecurityGroups", []):

        resources.append({

            "resource_id": group["GroupId"],

            "resource_type": "SECURITY_GROUP",

            "resource_name": group.get("GroupName"),

            "region": "ap-south-1",

            "resource_state": "available",

            "configuration": {

                "vpc_id": group.get("VpcId"),

                "description": group.get("Description"),

                "ip_permissions": group.get(
                    "IpPermissions", []
                ),

                "ip_permissions_egress": group.get(
                    "IpPermissionsEgress", []
                )

            }

        })

    return resources