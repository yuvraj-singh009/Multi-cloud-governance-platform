def scan_rds(session, region):
    rds = session.client("rds", region_name=region)
    resources = []
    paginator = rds.get_paginator("describe_db_instances")
    for page in paginator.paginate():
        for database in page.get("DBInstances", []):
            identifier = database["DBInstanceIdentifier"]
            resources.append({
                "resource_id": database.get("DbiResourceId", identifier),
                "resource_type": "RDS", "resource_name": identifier, "region": region,
                "resource_state": database.get("DBInstanceStatus"),
                "configuration": {
                    "engine": database.get("Engine"), "instance_class": database.get("DBInstanceClass"),
                    "storage": database.get("AllocatedStorage"),
                    "publicly_accessible": database.get("PubliclyAccessible")
                }
            })
    return resources
