
import os
import hmac

from flask import Response

from app.reports.csv_report import generate_csv_report

from flask import Flask, jsonify, request
from dotenv import load_dotenv

from app.database import get_supabase
from app.services.audit_service import audit_resources
from app.finops.cost_engine import estimate_monthly_waste

load_dotenv()

app = Flask(__name__)


def verify_internal_request():

    expected = os.getenv("INTERNAL_SERVICE_TOKEN", "")

    supplied = request.headers.get(
        "X-Internal-Token", ""
    )

    return bool(expected) and hmac.compare_digest(
        expected,
        supplied
    )


@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "service": "Cloud Governance Auditor",
        "status": "running"
    })


@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "service": "auditor-service",
        "status": "healthy"
    })


@app.route(
    "/api/v1/audit/<scan_id>",
    methods=["POST"]
)
def audit_scan(scan_id):

    if not verify_internal_request():

        return jsonify({
            "error": "Unauthorized internal request"
        }), 401

    db = get_supabase()

    scan_result = (
        db.table("scan_jobs")
        .select("id,status")
        .eq("id", scan_id)
        .execute()
    )

    if not scan_result.data:

        return jsonify({
            "error": "Scan not found"
        }), 404

    snapshot_result = (
        db.table("resource_snapshots")
        .select("*")
        .eq("scan_id", scan_id)
        .execute()
    )

    resources = snapshot_result.data

    findings = audit_resources(resources)

    violations_to_insert = []
    costs_to_insert = []

    resource_map = {
        item["resource_id"]: item
        for item in resources
    }

    for finding in findings:

        resource = resource_map[
            finding["resource_id"]
        ]

        violation = finding["violations"]

        snapshot_id = resource["id"]

        waste = estimate_monthly_waste(resource)

        violations_to_insert.append({

            "scan_id": scan_id,

            "resource_snapshot_id": snapshot_id,

            "policy_id": violation["policy_id"],

            "severity": violation["severity"],

            "description": violation["description"],

            "estimated_monthly_waste": waste

        })

        if waste > 0:

            costs_to_insert.append({

                "scan_id": scan_id,

                "resource_id": resource["resource_id"],

                "estimated_monthly_cost": waste,

                "estimated_monthly_waste": waste,

                "currency": "INR",

                "calculation_method": "Configurable rate estimate"

            })

    if violations_to_insert:

        db.table("policy_violations").insert(
            violations_to_insert
        ).execute()

    if costs_to_insert:

        db.table("cost_estimates").insert(
            costs_to_insert
        ).execute()

    return jsonify({

        "message": "Audit completed successfully",

        "scan_id": scan_id,

        "resources_audited": len(resources),

        "total_violations": len(findings),

        "potential_monthly_savings": sum(
            item["estimated_monthly_waste"]
            for item in costs_to_insert
        ),

        "violations": findings

    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )

@app.route(
    "/api/v1/reports/<scan_id>/csv",
    methods=["GET"]
)
def download_csv(scan_id):

    if not verify_internal_request():
        return jsonify({"error": "Unauthorized"}), 401

    db = get_supabase()

    result = (
        db.table("policy_violations")
        .select("*")
        .eq("scan_id", scan_id)
        .execute()
    )

    csv_data = generate_csv_report(result.data)

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            f"attachment; filename=audit-{scan_id}.csv"
        }
    )

