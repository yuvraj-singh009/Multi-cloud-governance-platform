
from app.policies.storage_rules import check_unattached_ebs
from app.policies.network_rules import (
    check_open_ssh,
    check_unused_elastic_ip
)
from app.policies.s3_rules import check_public_s3
from app.policies.ec2_rules import check_missing_tags


def evaluate_resource(resource):

    resource_type = resource.get("resource_type")

    violations = []

    if resource_type == "EBS":

        violations.extend(
            check_unattached_ebs(resource)
        )

    elif resource_type == "SECURITY_GROUP":

        violations.extend(
            check_open_ssh(resource)
        )

    elif resource_type == "ELASTIC_IP":

        violations.extend(
            check_unused_elastic_ip(resource)
        )

    elif resource_type == "S3":

        violations.extend(
            check_public_s3(resource)
        )

    elif resource_type == "EC2":

        violations.extend(
            check_missing_tags(resource)
        )

    elif resource_type == "RDS":

        config = resource.get("configuration", {})

        if config.get("publicly_accessible") is True:

            violations.append({
                "policy_id": "POL-007",
                "severity": "high",
                "description": (
                    "RDS database is publicly accessible"
                )
            })

    return violations


def audit_resources(resources):

    results = []

    for resource in resources:

        violations = evaluate_resource(resource)

        for violation in violations:

            results.append({

                "resource_id": resource["resource_id"],

                "resource_type": resource["resource_type"],

                "violations": violation

            })

    return results
