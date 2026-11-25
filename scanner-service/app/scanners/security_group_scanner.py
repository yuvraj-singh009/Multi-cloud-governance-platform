def scan_security_groups(session, region):
    ec2 = session.client("ec2", region_name=region)
    resources = []
    paginator = ec2.get_paginator("describe_security_groups")
    for page in paginator.paginate():
        for group in page.get("SecurityGroups", []):
            resources.append({
                "resource_id": group["GroupId"], "resource_type": "SECURITY_GROUP",
                "resource_name": group.get("GroupName"), "region": region,
                "resource_state": "available",
                "configuration": {
                    "vpc_id": group.get("VpcId"), "description": group.get("Description"),
                    "ip_permissions": group.get("IpPermissions", []),
                    "ip_permissions_egress": group.get("IpPermissionsEgress", [])
                }
            })
    return resources
