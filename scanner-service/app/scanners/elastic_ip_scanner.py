from app.config import get_aws_client


def scan_elastic_ips():

    ec2 = get_aws_client("ec2")

    response = ec2.describe_addresses()

    resources = []

    for address in response.get("Addresses", []):

        resources.append({

            "resource_id": address.get(
                "AllocationId",
                address.get("PublicIp")
            ),

            "resource_type": "ELASTIC_IP",

            "resource_name": address.get("PublicIp"),

            "region": "ap-south-1",

            "resource_state": (
                "associated"
                if address.get("AssociationId")
                else "unassociated"
            ),

            "configuration": {

                "public_ip": address.get("PublicIp"),

                "allocation_id": address.get("AllocationId"),

                "association_id": address.get("AssociationId"),

                "instance_id": address.get("InstanceId")

            }

        })

    return resources