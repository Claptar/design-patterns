"""
Exercise 3: Caching Proxy — and composing proxies

Continuing from Exercise 2. Report generation is expensive and the same
report is often requested many times. We want to cache the content so
that get_content() only calls through to the real service once per report.

Part A — implement CachingReportProxy.
Part B — compose all three proxies together.
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
# Subject interface — do not modify
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
# From Exercise 2 — provided, do not modify
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
# Part A — TODO: implement CachingReportProxy
# ---------------------------------------------------------------------------

class CachingReportProxy(ReportService):
    """
    A caching proxy for ReportService.

    Requirements:
    - Wrap any ReportService instance.
    - get_content() must call through to the wrapped service on the first
      call only. Store the result and return the cached value on all
      subsequent calls.
    - get_metadata() and delete_report() always forward without caching.
    - After delete_report() is called, the cache must be cleared so that
      the next get_content() call generates fresh content.

    Hint: think about what the cache key should be. The proxy wraps one
    service instance, so a single cached value (or None) is enough here.
    """

    def __init__(self, service: ReportService):
        # TODO
        raise NotImplementedError

    def get_metadata(self) -> ReportMetadata:
        # TODO
        raise NotImplementedError

    def get_content(self) -> str:
        # TODO
        raise NotImplementedError

    def delete_report(self) -> None:
        # TODO — forward, then clear the cache
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Part B — TODO: compose all three proxies
# ---------------------------------------------------------------------------

def build_report_service(
    report_id: str,
    title: str,
    author: str,
    role: str,
) -> ReportService:
    """
    Build a fully protected, cached ReportService.

    Layer order matters. Think about which proxy should be outermost and why.

    Hint: the protection proxy should be outermost so that unauthorised
    callers are rejected before any caching work happens. The caching proxy
    sits between protection and the real service so that permitted calls
    are cached.

    Expected stack (outer to inner):
        ProtectedReportProxy
            -> CachingReportProxy
                -> RealReportService
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests — do not modify
# ---------------------------------------------------------------------------

import pytest


# Part A tests

def test_content_is_cached():
    real = RealReportService("r1", "Report", "Alice")
    proxy = CachingReportProxy(real)

    proxy.get_content()
    proxy.get_content()
    proxy.get_content()

    assert real.generation_count == 1, (
        "get_content() must only call through to the real service once"
    )


def test_cached_value_is_correct():
    real = RealReportService("r1", "Report", "Alice")
    proxy = CachingReportProxy(real)

    result1 = proxy.get_content()
    result2 = proxy.get_content()

    assert result1 == result2


def test_metadata_always_forwards():
    real = RealReportService("r1", "Report", "Alice")
    proxy = CachingReportProxy(real)

    meta = proxy.get_metadata()
    assert meta.report_id == "r1"


def test_delete_clears_cache():
    real = RealReportService("r1", "Report", "Alice")
    proxy = CachingReportProxy(real)

    proxy.get_content()             # generates once
    proxy.delete_report()           # should clear the cache
    proxy.get_content()             # should generate again

    assert real.generation_count == 2, (
        "After delete_report(), get_content() must regenerate"
    )


def test_caching_proxy_is_a_report_service():
    real = RealReportService("r1", "Report", "Alice")
    assert isinstance(CachingReportProxy(real), ReportService)


# Part B tests

def test_composed_analyst_can_get_content():
    svc = build_report_service("r1", "Report", "Alice", role="analyst")
    content = svc.get_content()
    assert "PDF" in content


def test_composed_viewer_cannot_get_content():
    svc = build_report_service("r1", "Report", "Alice", role="viewer")
    with pytest.raises(PermissionError):
        svc.get_content()


def test_composed_caching_works(capsys):
    svc = build_report_service("r1", "Report", "Alice", role="analyst")

    svc.get_content()
    svc.get_content()
    svc.get_content()

    captured = capsys.readouterr()
    assert captured.out.count("Generating") == 1, (
        "Content should be generated once even through the composed stack"
    )


def test_composed_delete_clears_cache(capsys):
    svc = build_report_service("r1", "Report", "Alice", role="admin")

    svc.get_content()
    svc.delete_report()
    svc.get_content()

    captured = capsys.readouterr()
    assert captured.out.count("Generating") == 2, (
        "After delete, content must be regenerated"
    )


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
