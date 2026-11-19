import os

import httpx

from dotenv import load_dotenv

load_dotenv()


async def trigger_audit(scan_id):

    auditor_url = os.getenv("AUDITOR_URL")

    internal_token = os.getenv(
        "INTERNAL_SERVICE_TOKEN"
    )

    async with httpx.AsyncClient(
        timeout=60.0
    ) as client:

        response = await client.post(

            f"{auditor_url}/api/v1/audit/{scan_id}",

            headers={
                "X-Internal-Token": internal_token
            }

        )

        response.raise_for_status()

        return response.json()