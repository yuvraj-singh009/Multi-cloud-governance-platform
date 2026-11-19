import csv
import io


def generate_csv_report(violations):

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Policy ID",
        "Resource ID",
        "Severity",
        "Description",
        "Estimated Monthly Waste",
        "Status"
    ])

    for item in violations:

        writer.writerow([
            item.get("policy_id"),
            item.get("resource_snapshot_id"),
            item.get("severity"),
            item.get("description"),
            item.get("estimated_monthly_waste"),
            item.get("status")
        ])

    return output.getvalue()