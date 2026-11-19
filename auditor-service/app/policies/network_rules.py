def check_open_ssh(resource):

    violations = []

    config = resource.get("configuration", {})

    permissions = config.get(
        "ip_permissions", []
    )

    for permission in permissions:

        from_port = permission.get("FromPort")

        to_port = permission.get("ToPort")

        if from_port is None or to_port is None:
            continue

        if from_port <= 22 <= to_port:

            for ip_range in permission.get(
                "IpRanges", []
            ):

                if ip_range.get("CidrIp") == "0.0.0.0/0":

                    violations.append({

                        "policy_id": "POL-003",

                        "severity": "critical",

                        "description": (
                            "SSH access is allowed "
                            "from the entire internet"
                        )

                    })

    return violations

def check_unused_elastic_ip(resource):

    violations = []

    config = resource.get("configuration", {})

    if not config.get("association_id"):

        violations.append({

            "policy_id": "POL-002",

            "severity": "medium",

            "description": (
                "Elastic IP is allocated "
                "but not associated with a resource"
            )

        })

    return violations