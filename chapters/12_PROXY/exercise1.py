"""
Exercise 1: Virtual Proxy — lazy report loading

A ReportService generates PDF reports. Each report takes several seconds to
generate and consumes significant memory. The dashboard shows a list of
available reports (title and metadata only). The full report content is only
needed when the user clicks to download it.

Your task: implement a LazyReportProxy that delays generating the report
until get_content() is actually called.
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


@dataclass(frozen=True)
class Report:
    metadata: ReportMetadata
    content: str   # expensive to generate


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


# ---------------------------------------------------------------------------
# Real subject — do not modify
# ---------------------------------------------------------------------------

class RealReportService(ReportService):
    """Generates a report. Expensive — prints a message when it runs."""

    def __init__(self, report_id: str, title: str, author: str):
        self._metadata = ReportMetadata(
            report_id=report_id,
            title=title,
            author=author,
        )
        self._content: str | None = None

    def _generate(self) -> str:
        print(f"[RealReportService] Generating report '{self._metadata.title}'...")
        return f"PDF content for report {self._metadata.report_id}"

    def get_metadata(self) -> ReportMetadata:
        return self._metadata

    def get_content(self) -> str:
        if self._content is None:
            self._content = self._generate()
        return self._content


# ---------------------------------------------------------------------------
# TODO: implement LazyReportProxy
# ---------------------------------------------------------------------------

class LazyReportProxy(ReportService):
    """
    A virtual proxy for ReportService.

    Requirements:
    - Accept the same constructor arguments as RealReportService
      (report_id, title, author) but do NOT create a RealReportService yet.
    - get_metadata() must work WITHOUT creating the RealReportService.
      Hint: you already have everything you need from the constructor args.
    - get_content() must create the RealReportService on first call only,
      then delegate to it. On subsequent calls, reuse the same instance.
    - The caller must not be able to tell the difference between this proxy
      and a RealReportService.
    """

    def __init__(self, report_id: str, title: str, author: str):
        # TODO
        raise NotImplementedError

    def get_metadata(self) -> ReportMetadata:
        # TODO — must NOT trigger report generation
        raise NotImplementedError

    def get_content(self) -> str:
        # TODO — triggers generation on first call only
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests — do not modify
# ---------------------------------------------------------------------------

def test_metadata_does_not_trigger_generation(capsys):
    proxy = LazyReportProxy("r1", "Q1 Sales", "Alice")
    meta = proxy.get_metadata()

    captured = capsys.readouterr()
    assert "Generating" not in captured.out, (
        "get_metadata() must not trigger report generation"
    )
    assert meta.report_id == "r1"
    assert meta.title == "Q1 Sales"
    assert meta.author == "Alice"


def test_content_triggers_generation_once(capsys):
    proxy = LazyReportProxy("r2", "Q2 Sales", "Bob")

    content1 = proxy.get_content()
    content2 = proxy.get_content()

    captured = capsys.readouterr()
    assert captured.out.count("Generating") == 1, (
        "Report should be generated exactly once, not on every get_content() call"
    )
    assert content1 == content2


def test_proxy_is_a_report_service():
    proxy = LazyReportProxy("r3", "Annual", "Carol")
    assert isinstance(proxy, ReportService), (
        "LazyReportProxy must be a ReportService"
    )


def test_multiple_proxies_are_independent(capsys):
    proxy_a = LazyReportProxy("a", "Report A", "Alice")
    proxy_b = LazyReportProxy("b", "Report B", "Bob")

    # Only request content from proxy_a
    proxy_a.get_content()

    captured = capsys.readouterr()
    assert "Report A" in captured.out
    assert "Report B" not in captured.out, (
        "Requesting content from proxy_a must not trigger generation in proxy_b"
    )


if __name__ == "__main__":
    import pytest, sys
    sys.exit(pytest.main([__file__, "-v"]))
