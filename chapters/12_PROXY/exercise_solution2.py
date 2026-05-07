"""
Exercise 2 solution: Protection Proxy — role-based access control
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import pytest


# ---------------------------------------------------------------------------
# Domain objects
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ReportMetadata:
    report_id: str
    title: str
    author: str


# ---------------------------------------------------------------------------
# Extended subject interface
# ---------------------------------------------------------------------------

class ReportService(ABC):
    @abstractmethod
    def get_metadata(self) -> ReportMetadata:
        ...

    @abstractmethod
    def get_content(self) -> str:
        ...

    @abstractmethod
    def delete_report(self) -> None:
        ...


# ---------------------------------------------------------------------------
# Real subject
# ---------------------------------------------------------------------------

class RealReportService(ReportService):
    def __init__(self, report_id: str, title: str, author: str):
        self._metadata = ReportMetadata(
            report_id=report_id,
            title=title,
            author=author,
        )

    def get_metadata(self) -> ReportMetadata:
        return self._metadata

    def get_content(self) -> str:
        return f"PDF content for report {self._metadata.report_id}"

    def delete_report(self) -> None:
        print(f"[RealReportService] Report '{self._metadata.title}' deleted.")


# ---------------------------------------------------------------------------
# Access rules
# ---------------------------------------------------------------------------

ALLOWED_METHODS = {
    "viewer":  {"get_metadata"},
    "analyst": {"get_metadata", "get_content"},
    "admin":   {"get_metadata", "get_content", "delete_report"},
}


# ---------------------------------------------------------------------------
# Solution
# ---------------------------------------------------------------------------

class ProtectedReportProxy(ReportService):
    def __init__(self, service: ReportService, role: str):
        self._service = service
        self._role = role

    def _check(self, method_name: str) -> None:
        allowed = ALLOWED_METHODS.get(self._role, set())
        if method_name not in allowed:
            raise PermissionError(
                f"Role '{self._role}' is not allowed to call '{method_name}'."
            )

    def get_metadata(self) -> ReportMetadata:
        self._check("get_metadata")
        return self._service.get_metadata()

    def get_content(self) -> str:
        self._check("get_content")
        return self._service.get_content()

    def delete_report(self) -> None:
        self._check("delete_report")
        self._service.delete_report()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def make_service(role: str) -> ProtectedReportProxy:
    real = RealReportService("r1", "Annual Report", "Alice")
    return ProtectedReportProxy(real, role)


def test_viewer_can_get_metadata():
    assert make_service("viewer").get_metadata().title == "Annual Report"


def test_viewer_cannot_get_content():
    with pytest.raises(PermissionError):
        make_service("viewer").get_content()


def test_viewer_cannot_delete():
    with pytest.raises(PermissionError):
        make_service("viewer").delete_report()


def test_analyst_can_get_metadata():
    assert make_service("analyst").get_metadata() is not None


def test_analyst_can_get_content():
    assert "PDF" in make_service("analyst").get_content()


def test_analyst_cannot_delete():
    with pytest.raises(PermissionError):
        make_service("analyst").delete_report()


def test_admin_can_do_everything(capsys):
    svc = make_service("admin")
    svc.get_metadata()
    svc.get_content()
    svc.delete_report()
    assert "deleted" in capsys.readouterr().out


def test_unknown_role_is_denied():
    with pytest.raises(PermissionError):
        make_service("intern").get_metadata()


def test_proxy_is_a_report_service():
    assert isinstance(make_service("admin"), ReportService)


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
