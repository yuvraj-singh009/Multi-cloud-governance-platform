def scan_elastic_ips(session, region):
    ec2 = session.client("ec2", region_name=region)
    resources = []
    paginator = ec2.get_paginator("describe_addresses")
    for page in paginator.paginate():
        for address in page.get("Addresses", []):
            resource_id = address.get("AllocationId") or address.get("PublicIp")
            resources.append({
                "resource_id": resource_id, "resource_type": "ELASTIC_IP",
                "resource_name": address.get("PublicIp"), "region": region,
                "resource_state": "associated" if address.get("AssociationId") else "unassociated",
                "configuration": {
                    "public_ip": address.get("PublicIp"), "allocation_id": address.get("AllocationId"),
                    "association_id": address.get("AssociationId"), "instance_id": address.get("InstanceId")
                }
            })
    return resources
