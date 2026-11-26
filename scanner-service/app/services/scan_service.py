import asyncio
import os
from cryptography.fernet import Fernet
from app.services.aws_session import assume_customer_role

from app.scanners.ec2_scanner import scan_ec2
from app.scanners.ebs_scanner import scan_ebs
from app.scanners.s3_scanner import scan_s3
from app.scanners.rds_scanner import scan_rds
from app.scanners.security_group_scanner import scan_security_groups
from app.scanners.elastic_ip_scanner import scan_elastic_ips


async def run_full_scan(account):
    if account.get("connection_type") != "aws_assume_role":
        raise ValueError("Only verified cross-account AWS connections can be scanned.")
    if account.get("connection_status") != "connected" or not account.get("role_arn"):
        raise ValueError("AWS account connection is not verified.")
    encrypted_external_id = account.get("external_id_encrypted")
    key = os.getenv("CONNECTION_ENCRYPTION_KEY")
    if not encrypted_external_id or not key:
        raise ValueError("AWS connection encryption configuration is missing.")
    external_id = Fernet(key.encode()).decrypt(encrypted_external_id.encode()).decode()
    preferred_region = account.get("region") or os.getenv("AWS_REGION", "us-east-1")
    session = assume_customer_role(account["role_arn"], external_id, preferred_region)

    identity = session.client("sts").get_caller_identity()
    if identity.get("Account") != account.get("account_identifier"):
        raise ValueError("Assumed AWS role account does not match the connected account.")

    errors = []
    ec2 = session.client("ec2", region_name=preferred_region)
    try:
        regions = [item["RegionName"] for item in ec2.describe_regions(AllRegions=False).get("Regions", [])]
        if preferred_region in regions:
            regions.remove(preferred_region)
        regions.insert(0, preferred_region)
    except Exception as exc:
        regions = [preferred_region]
        errors.append({"service": "REGION_DISCOVERY", "region": preferred_region, "error": str(exc)})

    resources = []
    regional_scanners = [
        ("EC2", scan_ec2), ("EBS", scan_ebs), ("RDS", scan_rds),
        ("SECURITY_GROUP", scan_security_groups), ("ELASTIC_IP", scan_elastic_ips)
    ]
    for region in regions:
        for service_name, scanner in regional_scanners:
            try:
                found = await asyncio.to_thread(scanner, session, region)
                resources.extend(found)
            except Exception as exc:
                errors.append({"service": service_name, "region": region, "error": str(exc)})
        # S3 is global; list buckets only once and resolve each bucket's actual region.
    try:
        found = await asyncio.to_thread(scan_s3, session)
        resources.extend(found)
    except Exception as exc:
        errors.append({"service": "S3", "error": str(exc)})

    return {"resources": resources, "errors": errors, "total_resources": len(resources),
            "regions_scanned": regions, "verified_account_id": identity["Account"]}
