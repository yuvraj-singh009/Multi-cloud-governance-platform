from app.config import get_aws_client


def scan_ebs():

    ec2 = get_aws_client("ec2")

    response = ec2.describe_volumes()

    resources = []

    for volume in response.get("Volumes", []):

        attachments = volume.get("Attachments", [])

        resources.append({

            "resource_id": volume["VolumeId"],

            "resource_type": "EBS",

            "resource_name": volume["VolumeId"],

            "region": volume.get(
                "AvailabilityZone", ""
            )[:-1],

            "resource_state": volume.get("State"),

            "configuration": {

                "size_gb": volume.get("Size"),

                "volume_type": volume.get("VolumeType"),

                "encrypted": volume.get("Encrypted"),

                "attachments": attachments,

                "is_attached": len(attachments) > 0

            }

        })

    return resources