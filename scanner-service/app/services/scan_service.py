import asyncio

from app.scanners.ec2_scanner import scan_ec2
from app.scanners.ebs_scanner import scan_ebs
from app.scanners.s3_scanner import scan_s3
from app.scanners.rds_scanner import scan_rds
from app.scanners.security_group_scanner import scan_security_groups
from app.scanners.elastic_ip_scanner import scan_elastic_ips


async def run_full_scan():

    results = await asyncio.gather(

        asyncio.to_thread(scan_ec2),

        asyncio.to_thread(scan_ebs),

        asyncio.to_thread(scan_s3),

        asyncio.to_thread(scan_rds),

        asyncio.to_thread(scan_security_groups),

        asyncio.to_thread(scan_elastic_ips),

        return_exceptions=True

    )

    resources = []
    errors = []

    service_names = [
        "EC2",
        "EBS",
        "S3",
        "RDS",
        "SECURITY_GROUP",
        "ELASTIC_IP"
    ]

    for name, result in zip(service_names, results):

        if isinstance(result, Exception):

            errors.append({
                "service": name,
                "error": str(result)
            })

        else:

            resources.extend(result)

    return {
        "resources": resources,
        "errors": errors,
        "total_resources": len(resources)
    }