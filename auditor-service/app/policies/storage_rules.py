def check_unattached_ebs(resource):

    violations = []

    config = resource.get("configuration", {})

    attachments = config.get("attachments", [])

    if not attachments:

        violations.append({

            "policy_id": "POL-001",

            "severity": "medium",

            "description": (
                "EBS volume is not attached "
                "to any EC2 instance"
            )

        })

    return violations