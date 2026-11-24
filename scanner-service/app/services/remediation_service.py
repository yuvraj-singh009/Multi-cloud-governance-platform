def plan_remediation(
    action_type,
    resource_id,
    current_state
):

    if action_type == "REMOVE_PUBLIC_SSH":

        return {
            "resource_id": resource_id,
            "action": action_type,
            "dry_run": True,
            "description": (
                "Remove ingress rules exposing SSH "
                "to 0.0.0.0/0"
            ),
            "before_state": current_state
        }

    if action_type == "ADD_TAGS":

        return {
            "resource_id": resource_id,
            "action": action_type,
            "dry_run": True,
            "description": (
                "Add missing mandatory resource tags"
            ),
            "before_state": current_state
        }

    raise ValueError(
        "Unsupported remediation action"
    )