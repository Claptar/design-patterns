from __future__ import annotations

import csv
import html
import io
import json
from dataclasses import dataclass
from typing import Dict, Protocol, Sequence


@dataclass(frozen=True)
class ExportedFile:
    file_name: str
    content: str
    file_type: str


class PermissionChecker(Protocol):
    def check(self, user, report) -> None:
        ...


class ReportRowMapper(Protocol):
    def map(self, report) -> Sequence[dict]:
        ...


class ReportExporter(Protocol):
    def export(self, report, rows: Sequence[dict]) -> ExportedFile:
        ...


class AuditLogger(Protocol):
    def log_report_exported(self, report, user, export_type: str, url: str) -> None:
        ...


class FileStorage(Protocol):
    def upload(self, file_name: str, content: str, file_type: str) -> str:
        ...


class ReportExportPermissionChecker:
    def check(self, user, report) -> None:
        if user.role != "admin" and not user.can_export_reports:
            raise PermissionError("User cannot export reports")


class DefaultReportRowMapper:
    def map(self, report) -> Sequence[dict]:
        return [
            {
                "name": item.name,
                "amount": item.amount,
                "date": item.date.strftime("%Y-%m-%d"),
            }
            for item in report.items
        ]


class CsvReportExporter:
    def export(self, report, rows: Sequence[dict]) -> ExportedFile:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["name", "amount", "date"])
        writer.writeheader()
        writer.writerows(rows)

        return ExportedFile(
            file_name=f"{report.title}.csv",
            content=output.getvalue(),
            file_type="text/csv",
        )


class JsonReportExporter:
    def export(self, report, rows: Sequence[dict]) -> ExportedFile:
        return ExportedFile(
            file_name=f"{report.title}.json",
            content=json.dumps(list(rows)),
            file_type="application/json",
        )


class HtmlReportExporter:
    def export(self, report, rows: Sequence[dict]) -> ExportedFile:
        table_rows = []
        for row in rows:
            table_rows.append(
                "<tr>"
                f"<td>{html.escape(str(row['name']))}</td>"
                f"<td>{html.escape(str(row['amount']))}</td>"
                f"<td>{html.escape(str(row['date']))}</td>"
                "</tr>"
            )

        return ExportedFile(
            file_name=f"{report.title}.html",
            content="<table>" + "".join(table_rows) + "</table>",
            file_type="text/html",
        )


class ReportService:
    def __init__(
        self,
        permission_checker: PermissionChecker,
        row_mapper: ReportRowMapper,
        exporters: Dict[str, ReportExporter],
        audit_logger: AuditLogger,
        storage: FileStorage,
    ):
        self.permission_checker = permission_checker
        self.row_mapper = row_mapper
        self.exporters = exporters
        self.audit_logger = audit_logger
        self.storage = storage

    def export_report(self, report, export_type: str, user) -> str:
        self.permission_checker.check(user, report)
        rows = self.row_mapper.map(report)

        try:
            exporter = self.exporters[export_type]
        except KeyError as exc:
            raise ValueError("Unsupported export type") from exc

        exported_file = exporter.export(report, rows)

        url = self.storage.upload(
            exported_file.file_name,
            exported_file.content,
            exported_file.file_type,
        )

        self.audit_logger.log_report_exported(
            report=report,
            user=user,
            export_type=export_type,
            url=url,
        )

        return url
