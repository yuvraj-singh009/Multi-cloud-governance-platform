
import asyncio

from app.scanners.ec2_scanner import scan_ec2
from app.scanners.ebs_scanner import scan_ebs
from app.scanners.s3_scanner import scan_s3
from app.scanners.rds_scanner import scan_rds
from app.scanners.security_group_scanner import scan_security_groups
from app.scanners.elastic_ip_scanner import scan_elastic_ips


async def run_full_scan(connection_type=None):

    # Define supported scanners
    scanners = [
        ("EC2", scan_ec2),
        ("EBS", scan_ebs),
        ("S3", scan_s3),
        ("SECURITY_GROUP", scan_security_groups),
        ("ELASTIC_IP", scan_elastic_ips),
    ]

    # RDS is not available in your current LocalStack license
    if connection_type != "localstack":
        scanners.append(("RDS", scan_rds))

    print("\nStarting cloud resource discovery...")

    if connection_type == "localstack":
        print("Skipping RDS: Not supported by current LocalStack license.")

    # Execute scanners concurrently
    results = await asyncio.gather(
        *[
            asyncio.to_thread(scanner)
            for name, scanner in scanners
        ],
        return_exceptions=True
    )

    resources = []
    errors = []

    for (name, scanner), result in zip(scanners, results):

        if isinstance(result, Exception):

            errors.append({
                "service": name,
                "error": str(result)
            })

            print(f"[ERROR] {name}: {result}")

        else:

            resources.extend(result)

            print(
                f"[SUCCESS] {name}: {len(result)} resources discovered"
            )

    print("\nCloud discovery completed.")
    print("Total resources:", len(resources))
    print("Total errors:", len(errors))

    return {
        "resources": resources,
        "errors": errors,
        "total_resources": len(resources)
    }
