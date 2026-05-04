class ReportService:
    def export_report(self, report, export_type, user):
        # Check permissions
        if user.role != "admin" and not user.can_export_reports:
            raise PermissionError("User cannot export reports")

        # Prepare report data
        rows = []
        for item in report.items:
            rows.append({
                "name": item.name,
                "amount": item.amount,
                "date": item.date.strftime("%Y-%m-%d")
            })

        # Export report
        if export_type == "csv":
            content = "name,amount,date\n"
            for row in rows:
                content += f"{row['name']},{row['amount']},{row['date']}\n"

            file_name = report.title + ".csv"
            file_type = "text/csv"

        elif export_type == "json":
            import json
            content = json.dumps(rows)

            file_name = report.title + ".json"
            file_type = "application/json"

        elif export_type == "html":
            content = "<table>"
            for row in rows:
                content += (
                    f"<tr>"
                    f"<td>{row['name']}</td>"
                    f"<td>{row['amount']}</td>"
                    f"<td>{row['date']}</td>"
                    f"</tr>"
                )
            content += "</table>"

            file_name = report.title + ".html"
            file_type = "text/html"

        else:
            raise ValueError("Unsupported export type")

        # Save audit log
        audit_logger = AuditLogger()
        audit_logger.log({
            "event": "report_exported",
            "report_id": report.id,
            "user_id": user.id,
            "export_type": export_type
        })

        # Upload file
        storage = S3Storage()
        url = storage.upload(file_name, content, file_type)

        return url
