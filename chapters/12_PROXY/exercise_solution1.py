"""
Exercise 1 solution: Virtual Proxy — lazy report loading
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Domain objects
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ReportMetadata:
    report_id: str
    title: str
    author: str


@dataclass(frozen=True)
class Report:
    metadata: ReportMetadata
    content: str


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
# Solution
# ---------------------------------------------------------------------------

class LazyReportProxy(ReportService):
    def __init__(self, report_id: str, title: str, author: str):
        self._report_id = report_id
        self._title = title
        self._author = author
        self._real: RealReportService | None = None

    def _load(self) -> RealReportService:
        if self._real is None:
            self._real = RealReportService(
                self._report_id,
                self._title,
                self._author,
            )
        return self._real

    def get_metadata(self) -> ReportMetadata:
        # We have all the information we need without touching the real service.
        return ReportMetadata(
            report_id=self._report_id,
            title=self._title,
            author=self._author,
        )

    def get_content(self) -> str:
        return self._load().get_content()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_metadata_does_not_trigger_generation(capsys):
    proxy = LazyReportProxy("r1", "Q1 Sales", "Alice")
    meta = proxy.get_metadata()

    captured = capsys.readouterr()
    assert "Generating" not in captured.out
    assert meta.report_id == "r1"
    assert meta.title == "Q1 Sales"
    assert meta.author == "Alice"


def test_content_triggers_generation_once(capsys):
    proxy = LazyReportProxy("r2", "Q2 Sales", "Bob")

    content1 = proxy.get_content()
    content2 = proxy.get_content()

    captured = capsys.readouterr()
    assert captured.out.count("Generating") == 1
    assert content1 == content2


def test_proxy_is_a_report_service():
    proxy = LazyReportProxy("r3", "Annual", "Carol")
    assert isinstance(proxy, ReportService)


def test_multiple_proxies_are_independent(capsys):
    proxy_a = LazyReportProxy("a", "Report A", "Alice")
    proxy_b = LazyReportProxy("b", "Report B", "Bob")

    proxy_a.get_content()

    captured = capsys.readouterr()
    assert "Report A" in captured.out
    assert "Report B" not in captured.out


if __name__ == "__main__":
    import pytest, sys
    sys.exit(pytest.main([__file__, "-v"]))
