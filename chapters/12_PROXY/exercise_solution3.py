"""
Exercise 3 solution: Caching Proxy — and composing proxies
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
# Subject interface
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
        self._generation_count = 0

    @property
    def generation_count(self) -> int:
        return self._generation_count

    def get_metadata(self) -> ReportMetadata:
        return self._metadata

    def get_content(self) -> str:
        self._generation_count += 1
        print(f"[RealReportService] Generating '{self._metadata.title}' "
              f"(call #{self._generation_count})...")
        return f"PDF content for report {self._metadata.report_id}"

    def delete_report(self) -> None:
        print(f"[RealReportService] Report '{self._metadata.title}' deleted.")


# ---------------------------------------------------------------------------
# From Exercise 2
# ---------------------------------------------------------------------------

ALLOWED_METHODS = {
    "viewer":  {"get_metadata"},
    "analyst": {"get_metadata", "get_content"},
    "admin":   {"get_metadata", "get_content", "delete_report"},
}


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
# Solution: Part A
# ---------------------------------------------------------------------------

class CachingReportProxy(ReportService):
    def __init__(self, service: ReportService):
        self._service = service
        self._cached_content: str | None = None

    def get_metadata(self) -> ReportMetadata:
        return self._service.get_metadata()

    def get_content(self) -> str:
        if self._cached_content is None:
            self._cached_content = self._service.get_content()
        return self._cached_content

    def delete_report(self) -> None:
        self._service.delete_report()
        self._cached_content = None   # cache invalidated


# ---------------------------------------------------------------------------
# Solution: Part B
# ---------------------------------------------------------------------------

def build_report_service(
    report_id: str,
    title: str,
    author: str,
    role: str,
) -> ReportService:
    real = RealReportService(report_id, title, author)
    cached = CachingReportProxy(real)
    protected = ProtectedReportProxy(cached, role)
    return protected


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

# Part A

def test_content_is_cached():
    real = RealReportService("r1", "Report", "Alice")
    proxy = CachingReportProxy(real)
    proxy.get_content()
    proxy.get_content()
    proxy.get_content()
    assert real.generation_count == 1


def test_cached_value_is_correct():
    real = RealReportService("r1", "Report", "Alice")
    proxy = CachingReportProxy(real)
    assert proxy.get_content() == proxy.get_content()


def test_metadata_always_forwards():
    real = RealReportService("r1", "Report", "Alice")
    proxy = CachingReportProxy(real)
    assert proxy.get_metadata().report_id == "r1"


def test_delete_clears_cache():
    real = RealReportService("r1", "Report", "Alice")
    proxy = CachingReportProxy(real)
    proxy.get_content()
    proxy.delete_report()
    proxy.get_content()
    assert real.generation_count == 2


def test_caching_proxy_is_a_report_service():
    real = RealReportService("r1", "Report", "Alice")
    assert isinstance(CachingReportProxy(real), ReportService)


# Part B

def test_composed_analyst_can_get_content():
    svc = build_report_service("r1", "Report", "Alice", role="analyst")
    assert "PDF" in svc.get_content()


def test_composed_viewer_cannot_get_content():
    svc = build_report_service("r1", "Report", "Alice", role="viewer")
    with pytest.raises(PermissionError):
        svc.get_content()


def test_composed_caching_works(capsys):
    svc = build_report_service("r1", "Report", "Alice", role="analyst")
    svc.get_content()
    svc.get_content()
    svc.get_content()
    assert capsys.readouterr().out.count("Generating") == 1


def test_composed_delete_clears_cache(capsys):
    svc = build_report_service("r1", "Report", "Alice", role="admin")
    svc.get_content()
    svc.delete_report()
    svc.get_content()
    assert capsys.readouterr().out.count("Generating") == 2


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
