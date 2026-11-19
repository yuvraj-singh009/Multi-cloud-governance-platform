from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user, get_owned_account
from app.database import get_supabase

router = APIRouter(
    prefix="/api/v1/resources",
    tags=["Resources"]
)


@router.get("/")
def get_resources(
    account_id: UUID,
    user=Depends(get_current_user)
):

    get_owned_account(
        str(account_id),
        str(user.id)
    )

    db = get_supabase()

    scans = (
        db.table("scan_jobs")
        .select("id")
        .eq("account_id", str(account_id))
        .eq("status", "completed")
        .execute()
    )

    scan_ids = [item["id"] for item in scans.data]

    if not scan_ids:
        return {"resources": []}

    result = (
        db.table("resource_snapshots")
        .select("*")
        .in_("scan_id", scan_ids)
        .order("scanned_at", desc=True)
        .execute()
    )

    return {
        "resources": result.data
    }


@router.get("/health")
def resource_health():
    return {
        "message": "Resource API is working"
    }