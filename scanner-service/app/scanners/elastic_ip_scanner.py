def scan_elastic_ips(session, region):
    ec2 = session.client("ec2", region_name=region)
    resources = []

    # DescribeAddresses is not a pageable EC2 operation in botocore.
    # A single request returns the Elastic IP addresses for this region.
    response = ec2.describe_addresses()
    for address in response.get("Addresses", []):
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
