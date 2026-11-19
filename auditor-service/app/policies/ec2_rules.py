def check_missing_tags(resource):

    violations = []

    config = resource.get("configuration", {})

    tags = config.get("tags", {})

    required_tags = [
        "Environment",
        "Project",
        "Owner"
    ]

    missing = [
        tag for tag in required_tags
        if not tags.get(tag)
    ]

    if missing:

        violations.append({

            "policy_id": "POL-006",

            "severity": "medium",

            "description": (
                "Missing mandatory resource tags: "
                + ", ".join(missing)
            )

        })

    return violations