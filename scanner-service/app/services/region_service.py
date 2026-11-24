from app.services.aws_session import get_aws_client


def get_enabled_regions():

    ec2 = get_aws_client("ec2")

    response = ec2.describe_regions(
        AllRegions=False
    )

    return [
        region["RegionName"]
        for region in response["Regions"]
    ]

for region in get_enabled_regions():

    ec2 = get_aws_client(
        "ec2",
        region=region
    )

    # Run EC2, EBS, security group,
    # Elastic IP and other regional scanners.