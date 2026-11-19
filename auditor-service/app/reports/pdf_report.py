import io

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf_report(scan_id, violations):

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "Cloud Governance Audit Report",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"Scan ID: {scan_id}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    data = [[
        "Policy",
        "Severity",
        "Description",
        "Waste (INR)"
    ]]

    for item in violations:

        data.append([
            item.get("policy_id", ""),
            item.get("severity", ""),
            item.get("description", ""),
            str(item.get(
                "estimated_monthly_waste", 0
            ))
        ])

    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),

        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

        ("VALIGN", (0, 0), (-1, -1), "TOP"),

        ("FONTSIZE", (0, 0), (-1, -1), 8)

    ]))

    elements.append(table)

    document.build(elements)

    buffer.seek(0)

    return buffer


from flask import send_file

from app.reports.pdf_report import generate_pdf_report


@app.route(
    "/api/v1/reports/<scan_id>/pdf",
    methods=["GET"]
)
def download_pdf(scan_id):

    if not verify_internal_request():
        return jsonify({"error": "Unauthorized"}), 401

    db = get_supabase()

    result = (
        db.table("policy_violations")
        .select("*")
        .eq("scan_id", scan_id)
        .execute()
    )

    pdf_buffer = generate_pdf_report(
        scan_id,
        result.data
    )

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"audit-{scan_id}.pdf"
    )