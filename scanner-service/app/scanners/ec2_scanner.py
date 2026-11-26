def scan_ec2(session, region):
    ec2 = session.client("ec2", region_name=region)
    resources = []
    paginator = ec2.get_paginator("describe_instances")
    for page in paginator.paginate():
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                tags = {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
                resources.append({
                    "resource_id": instance["InstanceId"], "resource_type": "EC2",
                    "resource_name": tags.get("Name", instance["InstanceId"]),
                    "region": region, "resource_state": instance.get("State", {}).get("Name"),
                    "configuration": {
                        "instance_type": instance.get("InstanceType"), "image_id": instance.get("ImageId"),
                        "private_ip": instance.get("PrivateIpAddress"), "public_ip": instance.get("PublicIpAddress"),
                        "tags": tags
                    }
                })
    return resources
