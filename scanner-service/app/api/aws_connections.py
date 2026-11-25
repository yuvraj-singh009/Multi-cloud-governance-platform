"""Customer AWS onboarding using cross-account IAM roles."""
import os, re, secrets
from datetime import datetime, timezone
from uuid import UUID
from cryptography.fernet import Fernet, InvalidToken
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.auth import get_current_user, get_owned_account
from app.database import get_supabase
from app.services.aws_session import verify_customer_role

router = APIRouter(prefix="/api/v1/aws/connections", tags=["AWS Connections"])
ACCOUNT_ID_RE = re.compile(r"^\d{12}$")
ROLE_ARN_RE = re.compile(r"^arn:aws:iam::(\d{12}):role/[A-Za-z0-9+=,.@_/-]{1,512}$")

def _fernet():
    key = os.getenv("CONNECTION_ENCRYPTION_KEY")
    if not key:
        raise HTTPException(status_code=503, detail="AWS connection encryption is not configured")
    try:
        return Fernet(key.encode())
    except Exception as exc:
        raise HTTPException(status_code=503, detail="AWS connection encryption key is invalid") from exc

def _decrypt(value):
    try:
        return _fernet().decrypt(value.encode()).decode()
    except (InvalidToken, ValueError) as exc:
        raise HTTPException(status_code=500, detail="Stored AWS connection cannot be decrypted") from exc

class CreateConnection(BaseModel):
    account_name: str = Field(min_length=2, max_length=80)
    account_id: str
    region: str = Field(default="us-east-1", min_length=5, max_length=32)

class VerifyConnection(BaseModel):
    role_arn: str

@router.post("")
def create_connection(payload: CreateConnection, user=Depends(get_current_user)):
    if not ACCOUNT_ID_RE.fullmatch(payload.account_id):
        raise HTTPException(status_code=422, detail="AWS account ID must contain exactly 12 digits")
    if not re.fullmatch(r"[a-z0-9-]{5,32}", payload.region):
        raise HTTPException(status_code=422, detail="Invalid AWS region format")
    external_id = "cgp-" + secrets.token_urlsafe(36)
    encrypted = _fernet().encrypt(external_id.encode()).decode()
    try:
        result = get_supabase().table("cloud_accounts").insert({
            "user_id": str(user.id), "account_name": payload.account_name.strip(),
            "provider": "AWS", "account_identifier": payload.account_id,
            "region": payload.region, "connection_type": "aws_assume_role",
            "connection_status": "pending", "external_id_encrypted": encrypted,
        }).execute()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not create connection. Apply the database migration and retry.") from exc
    account = result.data[0]
    return {"connection_id": account["id"], "external_id": external_id,
            "account_id": payload.account_id, "status": "pending",
            "instructions": "Save this External ID; it is shown once. Create the customer IAM role and verify using its Role ARN."}

@router.post("/{connection_id}/verify")
def verify_connection(connection_id: UUID, payload: VerifyConnection, user=Depends(get_current_user)):
    account = get_owned_account(str(connection_id), str(user.id))
    if account.get("connection_type") != "aws_assume_role":
        raise HTTPException(status_code=400, detail="This account is not configured for AWS role connection")
    match = ROLE_ARN_RE.fullmatch(payload.role_arn or "")
    if not match or match.group(1) != account.get("account_identifier"):
        raise HTTPException(status_code=422, detail="Role ARN account ID must match the connected AWS account ID")
    if not account.get("external_id_encrypted"):
        raise HTTPException(status_code=409, detail="External ID is missing. Create a new connection.")
    external_id = _decrypt(account["external_id_encrypted"])
    try:
        identity = verify_customer_role(payload.role_arn, external_id, account["account_identifier"])
    except Exception as exc:
        raise HTTPException(status_code=400, detail="AWS role verification failed. Check role trust, External ID, platform AssumeRole permission and role permissions.") from exc
    get_supabase().table("cloud_accounts").update({
        "role_arn": payload.role_arn, "connection_status": "connected",
        "verified_at": datetime.now(timezone.utc).isoformat()
    }).eq("id", str(connection_id)).eq("user_id", str(user.id)).execute()
    return {"connection_id": str(connection_id), "status": "connected", "verified_account_id": identity["account_id"]}

@router.get("")
def list_connections(user=Depends(get_current_user)):
    result = get_supabase().table("cloud_accounts").select(
        "id,account_name,provider,account_identifier,region,connection_type,connection_status,verified_at,created_at"
    ).eq("user_id", str(user.id)).order("created_at", desc=True).execute()
    return {"connections": result.data or []}

@router.delete("/{connection_id}")
def disconnect(connection_id: UUID, user=Depends(get_current_user)):
    get_owned_account(str(connection_id), str(user.id))
    get_supabase().table("cloud_accounts").delete().eq("id", str(connection_id)).eq("user_id", str(user.id)).execute()
    return {"status": "disconnected"}
