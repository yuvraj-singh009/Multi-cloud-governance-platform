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
async def start_scan(account_id: UUID, user=Depends(get_current_user)):
    db = get_supabase()
    account = get_owned_account(str(account_id), str(user.id))

    if account.get("connection_type") != "aws_assume_role":
        raise HTTPException(status_code=400, detail="This scan endpoint requires a cross-account AWS connection.")
    if account.get("connection_status") != "connected" or not account.get("role_arn"):
        raise HTTPException(status_code=409, detail="Verify the AWS IAM role before starting a scan.")

    scan = db.table("scan_jobs").insert({
        "account_id": str(account_id),
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat()
    }).execute()
    scan_id = scan.data[0]["id"]

    try:
        result = await run_full_scan(account)
        snapshots = []
        for resource in result["resources"]:
            snapshots.append({
                "scan_id": scan_id,
                "resource_id": resource["resource_id"],
                "resource_type": resource["resource_type"],
                "resource_name": resource["resource_name"],
                "region": resource["region"],
                "resource_state": resource["resource_state"],
                "configuration": json.loads(json.dumps(resource["configuration"], default=str))
            })

        if snapshots:
            db.table("resource_snapshots").insert(snapshots).execute()

        # Preserve the existing scan status vocabulary. A scan with any collection
        # errors is marked failed, while its collected snapshots remain stored.
        status = "completed" if not result["errors"] else "failed"
        db.table("scan_jobs").update({
            "status": status,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "resources_scanned": result["total_resources"],
            "error_message": json.dumps(result["errors"]) if result["errors"] else None
        }).eq("id", scan_id).execute()

        audit_result = None
        audit_error = None
        if status == "completed":
            try:
                audit_result = await trigger_audit(scan_id)
            except Exception:
                # An auditor outage must not erase a successfully completed scan.
                audit_error = "Scan completed, but the audit service could not process this scan."

        return {
            "message": "Cloud scan completed" if status == "completed" else "Cloud scan completed with collection errors",
            "scan_id": scan_id,
            "account_name": account["account_name"],
            "verified_account_id": result["verified_account_id"],
            "regions_scanned": result["regions_scanned"],
            "total_resources": result["total_resources"],
            "status": status,
            "audit": audit_result,
            "audit_error": audit_error,
            "errors": result["errors"]
        }

    except Exception as error:
        db.table("scan_jobs").update({
            "status": "failed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "error_message": "Scan failed. Check backend logs for details."
        }).eq("id", scan_id).execute()
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(error)}")
