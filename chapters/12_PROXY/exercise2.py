"""
Exercise 2: Protection Proxy — role-based access control

Continuing from Exercise 1. The dashboard now has multiple user roles.
Not every role is allowed to access every report type.

Access rules:
  - "viewer"  : may call get_metadata() only
  - "analyst" : may call get_metadata() and get_content()
  - "admin"   : may call get_metadata(), get_content(), and delete_report()

Your task: implement a ProtectedReportProxy that enforces these rules.

Notice that delete_report() is a new method that does not exist on the
original ReportService. You will need to extend the interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Domain objects — do not modify
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ReportMetadata:
    report_id: str
    title: str
    author: str


# ---------------------------------------------------------------------------
# Extended subject interface — do not modify
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
# Real subject — do not modify
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
# TODO: implement ProtectedReportProxy
# ---------------------------------------------------------------------------

# Access rules:
ALLOWED_METHODS = {
    "viewer":  {"get_metadata"},
    "analyst": {"get_metadata", "get_content"},
    "admin":   {"get_metadata", "get_content", "delete_report"},
}


class ProtectedReportProxy(ReportService):
    """
    A protection proxy for ReportService.

    Requirements:
    - Wrap any ReportService instance and a role string.
    - Before forwarding any call, check that the current role is allowed
      to call that method. Raise PermissionError with a clear message if not.
    - Do not duplicate the access rules in each method — use ALLOWED_METHODS
      and a single helper to keep the logic in one place.
    - All three methods (get_metadata, get_content, delete_report) must be
      present and enforced.
    """

    def __init__(self, service: ReportService, role: str):
        # TODO
        raise NotImplementedError

    def _check(self, method_name: str) -> None:
        # TODO: raise PermissionError if the role cannot call method_name
        raise NotImplementedError

    def get_metadata(self) -> ReportMetadata:
        # TODO
        raise NotImplementedError

    def get_content(self) -> str:
        # TODO
        raise NotImplementedError

    def delete_report(self) -> None:
        # TODO
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests — do not modify
# ---------------------------------------------------------------------------

import pytest


def make_service(role: str) -> ProtectedReportProxy:
    real = RealReportService("r1", "Annual Report", "Alice")
    return ProtectedReportProxy(real, role)


# viewer
def test_viewer_can_get_metadata():
    svc = make_service("viewer")
    meta = svc.get_metadata()
    assert meta.title == "Annual Report"


def test_viewer_cannot_get_content():
    svc = make_service("viewer")
    with pytest.raises(PermissionError):
        svc.get_content()


def test_viewer_cannot_delete():
    svc = make_service("viewer")
    with pytest.raises(PermissionError):
        svc.delete_report()


# analyst
def test_analyst_can_get_metadata():
    svc = make_service("analyst")
    assert svc.get_metadata() is not None


def test_analyst_can_get_content():
    svc = make_service("analyst")
    assert "PDF" in svc.get_content()


def test_analyst_cannot_delete():
    svc = make_service("analyst")
    with pytest.raises(PermissionError):
        svc.delete_report()


# admin
def test_admin_can_do_everything(capsys):
    svc = make_service("admin")
    svc.get_metadata()
    svc.get_content()
    svc.delete_report()
    captured = capsys.readouterr()
    assert "deleted" in captured.out


# unknown role
def test_unknown_role_is_denied():
    svc = make_service("intern")
    with pytest.raises(PermissionError):
        svc.get_metadata()


def test_proxy_is_a_report_service():
    svc = make_service("admin")
    assert isinstance(svc, ReportService)


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
