import json
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user, get_owned_account
from app.database import get_supabase
from app.services.auditor_client import trigger_audit
from app.services.scan_service import run_full_scan

router = APIRouter(prefix="/api/v1/scans", tags=["Scans"])


@router.post("/{account_id}")
async def start_scan(
    account_id: UUID,
    user=Depends(get_current_user)
):
    db = get_supabase()

    account = get_owned_account(
        str(account_id),
        str(user.id)
    )

    scan = db.table("scan_jobs").insert({
        "account_id": str(account_id),
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat()
    }).execute()

    scan_id = scan.data[0]["id"]

    try:
        result = await run_full_scan(
    connection_type=account.get("connection_type")
)

        snapshots = []
        for resource in result["resources"]:
            snapshots.append({
                "scan_id": scan_id,
                "resource_id": resource["resource_id"],
                "resource_type": resource["resource_type"],
                "resource_name": resource["resource_name"],
                "region": resource["region"],
                "resource_state": resource["resource_state"],
                "configuration": json.loads(
                    json.dumps(
                        resource["configuration"],
                        default=str
                    )
                )
            })

        if snapshots:
            db.table("resource_snapshots").insert(
                snapshots
            ).execute()

        status = (
            "completed"
            if not result["errors"]
            else "failed"
        )

        db.table("scan_jobs").update({
            "status": status,
            "completed_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "resources_scanned": result[
                "total_resources"
            ],
            "error_message": json.dumps(
                result["errors"]
            ) if result["errors"] else None
        }).eq("id", scan_id).execute()

        # Trigger the audit after saving snapshots and updating scan status
        audit_result = await trigger_audit(scan_id)

        return {
            "message": "Cloud scan and audit completed",
            "scan_id": scan_id,
            "account_name": account["account_name"],
            "total_resources": result["total_resources"],
            "audit": audit_result,
            "errors": result["errors"]
        }

    except Exception as error:
        db.table("scan_jobs").update({
            "status": "failed",
            "completed_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "error_message": str(error)
        }).eq("id", scan_id).execute()

        raise HTTPException(
            status_code=500,
            detail=f"Scan failed: {str(error)}"
        )