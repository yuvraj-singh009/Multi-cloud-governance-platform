from app.config import get_aws_client


def scan_ec2():

    ec2 = get_aws_client("ec2")

    response = ec2.describe_instances()

    resources = []

    for reservation in response.get("Reservations", []):

        for instance in reservation.get("Instances", []):

            tags = {
                tag["Key"]: tag["Value"]
                for tag in instance.get("Tags", [])
            }

            resources.append({

                "resource_id": instance["InstanceId"],

                "resource_type": "EC2",

                "resource_name": tags.get(
                    "Name",
                    instance["InstanceId"]
                ),

                "region": instance.get(
                    "Placement", {}
                ).get("AvailabilityZone", "")[:-1],

                "resource_state": instance.get(
                    "State", {}
                ).get("Name"),

                "configuration": {

                    "instance_type": instance.get(
                        "InstanceType"
                    ),

                    "image_id": instance.get(
                        "ImageId"
                    ),

                    "private_ip": instance.get(
                        "PrivateIpAddress"
                    ),

                    "public_ip": instance.get(
                        "PublicIpAddress"
                    ),

                    "tags": tags
                }

            })

    return resources