from app.config import get_aws_client


def scan_rds():

    rds = get_aws_client("rds")

    response = rds.describe_db_instances()

    resources = []

    for database in response.get(
        "DBInstances", []
    ):

        resources.append({

            "resource_id": database.get(
                "DbiResourceId",
                database["DBInstanceIdentifier"]
            ),

            "resource_type": "RDS",

            "resource_name": database[
                "DBInstanceIdentifier"
            ],

            "region": database.get(
                "AvailabilityZone", ""
            )[:-1],

            "resource_state": database.get(
                "DBInstanceStatus"
            ),

            "configuration": {

                "engine": database.get("Engine"),

                "instance_class": database.get(
                    "DBInstanceClass"
                ),

                "storage": database.get(
                    "AllocatedStorage"
                ),

                "publicly_accessible": database.get(
                    "PubliclyAccessible"
                )

            }

        })

    return resources