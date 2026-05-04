# SOLID Exercise2: Report Exporting

## Scenario

A business dashboard lets users export reports. The current implementation looks like this:

```python
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
```

## Your critique

- Permission checking, report generation, and report saving/uploading should be separate responsibilities. This suggests a Single Responsibility Principle violation.
- Export types are handled with an `if`/`elif` chain. This suggests an Open/Closed Principle violation.
- Specific implementations are hard-coded for exporting, auditing, and uploading behavior. This suggests a Dependency Inversion Principle violation.

## Fuller critique

You caught the three biggest issues: **SRP**, **OCP**, and **DIP**.

### Overall verdict

The method is doing too much:

```python
class ReportService:
    def export_report(self, report, export_type, user):
        # permissions
        # data preparation
        # format-specific export
        # audit logging
        # storage upload
        # return URL
```

The basic workflow is reasonable:

```text
check permission
prepare report data
export into a format
audit the action
upload the file
return the URL
```

But the problem is that `ReportService` owns the details of every step. As the app grows, this method will become harder to change, harder to test, and easier to break.

## 1. Single Responsibility Principle

`ReportService.export_report()` currently handles several responsibilities:

| Responsibility | Example code |
|---|---|
| Permission checking | `if user.role != "admin" and not user.can_export_reports` |
| Report data transformation | building `rows` |
| CSV formatting | `if export_type == "csv"` |
| JSON formatting | `elif export_type == "json"` |
| HTML formatting | `elif export_type == "html"` |
| Audit logging | `AuditLogger().log(...)` |
| File uploading | `S3Storage().upload(...)` |

That gives it many reasons to change.

| Change request | Class/method affected |
|---|---|
| Permission rules change | `ReportService.export_report()` |
| Report row shape changes | `ReportService.export_report()` |
| CSV escaping rules change | `ReportService.export_report()` |
| Add PDF export | `ReportService.export_report()` |
| Audit event schema changes | `ReportService.export_report()` |
| Switch S3 to Azure Blob Storage | `ReportService.export_report()` |

That is a strong SRP violation.

A cleaner design might split responsibilities like this:

```python
class ReportExportPermission:
    def check(self, user, report):
        ...

class ReportDataMapper:
    def map(self, report):
        ...

class ReportExporter:
    def export(self, rows, report):
        ...

class AuditLogger:
    def log_report_exported(self, report, user, export_type):
        ...

class FileStorage:
    def upload(self, file_name, content, file_type):
        ...
```

The service can still coordinate the workflow. SRP does not mean `export_report()` can only call one thing. It means it should not personally own all the unrelated details.

## 2. Open/Closed Principle

The export branch is an OCP issue:

```python
if export_type == "csv":
    ...
elif export_type == "json":
    ...
elif export_type == "html":
    ...
else:
    raise ValueError("Unsupported export type")
```

Every new format requires editing this existing method.

Adding PDF, XLSX, XML, Markdown, or Google Sheets export would require modifying `ReportService`.

A better design is to create separate exporter implementations:

```python
class CsvReportExporter:
    def export(self, rows, report):
        ...

class JsonReportExporter:
    def export(self, rows, report):
        ...

class HtmlReportExporter:
    def export(self, rows, report):
        ...
```

Then use a registry:

```python
exporters = {
    "csv": CsvReportExporter(),
    "json": JsonReportExporter(),
    "html": HtmlReportExporter(),
}
```

Now adding PDF means adding a new exporter and registering it, not rewriting the main export workflow.

## 3. Dependency Inversion Principle

This code directly creates concrete dependencies:

```python
audit_logger = AuditLogger()
storage = S3Storage()
```

That tightly couples `ReportService` to specific infrastructure.

Problems:

```text
You cannot easily replace S3 with local storage, Azure, GCS, or a fake test storage.
You cannot easily test without touching real storage unless you patch constructors.
You cannot change audit logging implementation without editing ReportService.
High-level report workflow depends directly on low-level technical details.
```

A better design injects dependencies:

```python
class ReportService:
    def __init__(self, permission_checker, data_mapper, exporters, audit_logger, storage):
        self.permission_checker = permission_checker
        self.data_mapper = data_mapper
        self.exporters = exporters
        self.audit_logger = audit_logger
        self.storage = storage
```

That makes the service easier to test and easier to change.

## 4. Interface Segregation Principle

There is no obvious ISP violation in the original code because no interface is shown.

But ISP matters in the refactor. A bad refactor would be one huge dependency:

```python
class ReportExportInfrastructure:
    def check_permissions(self, user, report):
        ...

    def map_report_data(self, report):
        ...

    def export_csv(self, rows):
        ...

    def export_json(self, rows):
        ...

    def export_html(self, rows):
        ...

    def log_audit_event(self, event):
        ...

    def upload_to_s3(self, file_name, content, file_type):
        ...
```

That would just move the mess into a bigger abstraction.

A better refactor uses small, focused contracts:

```python
class PermissionChecker:
    def check(self, user, report):
        ...

class ReportDataMapper:
    def map(self, report):
        ...

class ReportExporter:
    def export(self, rows, report):
        ...

class AuditLogger:
    def log_report_exported(self, report, user, export_type):
        ...

class FileStorage:
    def upload(self, file_name, content, file_type):
        ...
```

The current code does not directly violate ISP, but a careless refactor could. Avoid replacing one large method with one large interface.

## 5. Liskov Substitution Principle

There is no direct LSP issue in the current code because no inheritance/subtyping is shown.

But once exporter abstractions are introduced, LSP matters. If all exporters share this contract:

```python
class ReportExporter:
    def export(self, rows, report):
        """Return an ExportedFile."""
```

Then every exporter should honor that contract.

This would be suspicious:

```python
class PdfReportExporter(ReportExporter):
    def export(self, rows, report):
        if len(rows) > 1000:
            raise ValueError("PDF export supports only 1000 rows")
```

That might be okay only if the parent contract allows exporters to reject unsupported reports. If the service assumes all exporters can export any valid report, then `PdfReportExporter` weakens the contract.

## 6. Other design smells

### The method mixes business logic and infrastructure

Permission checks are business/application logic. Audit logging and S3 upload are infrastructure concerns. The method mixes all of these.

### The data preparation may belong separately

This block is doing report-to-export-row mapping:

```python
rows = []
for item in report.items:
    rows.append({
        "name": item.name,
        "amount": item.amount,
        "date": item.date.strftime("%Y-%m-%d")
    })
```

It could grow to include currency formatting, timezone handling, localized dates, hidden columns, user-specific fields, privacy masking, and rounding rules.

### CSV generation is naive

This line is risky:

```python
content += f"{row['name']},{row['amount']},{row['date']}\n"
```

It does not handle commas, quotes, newlines, encoding concerns, or spreadsheet formula injection risks.

### HTML generation is unsafe

This code inserts values directly into HTML:

```python
f"<td>{row['name']}</td>"
```

A proper HTML exporter should escape values.

### Audit and upload ordering should be considered

Current order:

```text
generate content
log audit event
upload file
return URL
```

The audit event is written before upload succeeds. Depending on requirements, better events might be `report_export_requested`, `report_export_succeeded`, and `report_export_failed`.

### Error handling is unclear

The code does not define what should happen if audit logging, S3 upload, JSON serialization, or export generation fails.

### Performance could become an issue

Repeated string concatenation may be fine for small reports but inefficient for large ones. Dedicated exporters could use `join`, streaming output, temporary files, or background jobs.

## 7. Which parts are okay?

The high-level sequence is okay:

```text
check permission
prepare data
export
audit
upload
return URL
```

The permission check is simple and readable. For a small app, inline permission logic might be acceptable.

The unsupported export type error is also okay conceptually. The problem is not rejecting unsupported types; the problem is hard-coding all supported types inside the service.


## 8. Middle-ground refactor

A full refactor can be useful, but it may be too much if this is still a small internal tool. A middle-ground refactor keeps the permission check and row mapping inside `ReportService` as private helper methods, while still extracting the parts most likely to change: exporters, storage, and audit logging.

This gives you the biggest SOLID benefits without creating too many classes too early.

```python
class ReportService:
    def __init__(self, exporters, storage, audit_logger):
        self.exporters = exporters
        self.storage = storage
        self.audit_logger = audit_logger

    def export_report(self, report, export_type, user):
        self._check_permission(user)
        rows = self._build_rows(report)

        try:
            exporter = self.exporters[export_type]
        except KeyError:
            raise ValueError("Unsupported export type")

        exported_file = exporter.export(report, rows)

        url = self.storage.upload(
            exported_file.file_name,
            exported_file.content,
            exported_file.file_type
        )

        self.audit_logger.log_report_exported(report, user, export_type, url)

        return url

    def _check_permission(self, user):
        if user.role != "admin" and not user.can_export_reports:
            raise PermissionError("User cannot export reports")

    def _build_rows(self, report):
        return [
            {
                "name": item.name,
                "amount": item.amount,
                "date": item.date.strftime("%Y-%m-%d"),
            }
            for item in report.items
        ]
```

This version improves the original design because:

- **OCP improves**: adding a new export format means adding a new exporter and registering it.
- **DIP improves**: storage and audit logging are injected instead of created inside the method.
- **SRP improves somewhat**: format generation, upload details, and audit details are separated.

It is not as clean as the full refactor because `ReportService` still owns permission rules and row mapping. That may be acceptable when those rules are simple and stable. If permissions or mapping become complex, extract them later.

Use this middle-ground approach when you want to reduce the worst coupling without turning a small feature into a large object graph.

## 9. Balanced refactor

A balanced refactor would make `ReportService` read like a workflow:

```text
check permission
map report data
choose exporter
export file
upload file
log audit event
return URL
```

The fixed implementation is saved here: [exercise2_fixed.py](exercise2_fixed.py)

## Summary

| Principle | Critique |
|---|---|
| SRP | Violated. The service handles permissions, mapping, exporting, auditing, uploading, and dependency creation. |
| OCP | Violated. New export types require editing `ReportService`. |
| DIP | Violated. The service directly creates `AuditLogger` and `S3Storage`. |
| ISP | Not directly visible. Be careful not to introduce one giant interface during refactoring. |
| LSP | Not directly visible. Matters once exporter abstractions are introduced. |

A good design keeps the workflow in `ReportService`, but moves the details of permissions, mapping, format generation, auditing, and storage into focused collaborators.
