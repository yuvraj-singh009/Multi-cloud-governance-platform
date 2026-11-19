def check_public_s3(resource):

    violations = []

    config = resource.get("configuration", {})

    policy = config.get("policy")

    if not isinstance(policy, dict):
        return violations

    statements = policy.get("Statement", [])

    if isinstance(statements, dict):
        statements = [statements]

    for statement in statements:

        if statement.get("Effect") != "Allow":
            continue

        principal = statement.get("Principal")

        public_principal = (
            principal == "*"
            or (
                isinstance(principal, dict)
                and principal.get("AWS") == "*"
            )
        )

        if not public_principal:
            continue

        actions = statement.get("Action", [])

        if isinstance(actions, str):
            actions = [actions]

        public_read = any(
            action in ["s3:GetObject", "s3:*", "*"]
            for action in actions
        )

        if public_read:

            violations.append({

                "policy_id": "POL-004",

                "severity": "critical",

                "description": (
                    "S3 bucket policy grants "
                    "public read access"
                )

            })

    return violations