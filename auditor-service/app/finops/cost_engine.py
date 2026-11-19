import os

from dotenv import load_dotenv

load_dotenv()

EBS_RATE = float(
    os.getenv("COST_EBS_GB_MONTH_INR", "30")
)

ELASTIC_IP_RATE = float(
    os.getenv("COST_ELASTIC_IP_MONTH_INR", "250")
)


def estimate_monthly_waste(resource):

    resource_type = resource.get("resource_type")

    config = resource.get("configuration", {})

    if resource_type == "EBS":

        if not config.get("attachments"):

            size = config.get("size_gb", 0)

            return float(size) * EBS_RATE

    if resource_type == "ELASTIC_IP":

        if not config.get("association_id"):

            return ELASTIC_IP_RATE

    return 0.0