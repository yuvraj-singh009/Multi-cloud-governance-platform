def scan_ebs(session, region):
    ec2 = session.client("ec2", region_name=region)
    resources = []
    paginator = ec2.get_paginator("describe_volumes")
    for page in paginator.paginate():
        for volume in page.get("Volumes", []):
            attachments = volume.get("Attachments", [])
            resources.append({
                "resource_id": volume["VolumeId"], "resource_type": "EBS",
                "resource_name": volume["VolumeId"], "region": region,
                "resource_state": volume.get("State"),
                "configuration": {
                    "size_gb": volume.get("Size"), "volume_type": volume.get("VolumeType"),
                    "encrypted": volume.get("Encrypted"), "attachments": attachments,
                    "is_attached": bool(attachments),
                    "tags": {tag["Key"]: tag["Value"] for tag in volume.get("Tags", [])}
                }
            })
    return resources
