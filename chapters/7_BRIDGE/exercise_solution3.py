"""
Bridge Exercise 3: Solution
"""

from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# Implementor interface
# ---------------------------------------------------------------------------

class Renderer(ABC):
    @abstractmethod
    def render_title(self, title: str) -> str: ...

    @abstractmethod
    def render_row(self, label: str, value: str) -> str: ...

    @abstractmethod
    def finish(self, parts: list[str]) -> str: ...


# ---------------------------------------------------------------------------
# Concrete renderers
# ---------------------------------------------------------------------------

class HtmlRenderer(Renderer):
    def render_title(self, title: str) -> str:
        return f"<h1>{title}</h1>"

    def render_row(self, label: str, value: str) -> str:
        return f"<tr><td>{label}</td><td>{value}</td></tr>"

    def finish(self, parts: list[str]) -> str:
        return "<table>" + "".join(parts) + "</table>"


class CsvRenderer(Renderer):
    def render_title(self, title: str) -> str:
        return f"# {title}"

    def render_row(self, label: str, value: str) -> str:
        return f"{label},{value}"

    def finish(self, parts: list[str]) -> str:
        return "\n".join(parts)


class MarkdownRenderer(Renderer):
    def render_title(self, title: str) -> str:
        return f"## {title}"

    def render_row(self, label: str, value: str) -> str:
        return f"| {label} | {value} |"

    def finish(self, parts: list[str]) -> str:
        return "\n".join([parts[0], "|---|---|", *parts[1:]])


# ---------------------------------------------------------------------------
# Abstraction base and concrete reports
# ---------------------------------------------------------------------------

class Report(ABC):
    def __init__(self, renderer: Renderer):
        self._renderer = renderer

    @abstractmethod
    def generate(self, data: dict) -> str: ...

    def switch_renderer(self, renderer: Renderer) -> None:
        self._renderer = renderer


class SummaryReport(Report):
    def generate(self, data: dict) -> str:
        parts = [self._renderer.render_title("Summary")]
        parts.append(self._renderer.render_row("Total", str(data.get("total", 0))))
        parts.append(self._renderer.render_row("Count", str(data.get("count", 0))))
        return self._renderer.finish(parts)


class DetailedReport(Report):
    def generate(self, data: dict) -> str:
        parts = [self._renderer.render_title("Detailed Report")]
        for key, value in data.items():
            parts.append(self._renderer.render_row(key, str(value)))
        return self._renderer.finish(parts)


# ---------------------------------------------------------------------------
# MultiRenderer
# ---------------------------------------------------------------------------

class MultiRenderer(Renderer):
    def __init__(self, *renderers: Renderer):
        self._renderers = renderers

    def render_title(self, title: str) -> str:
        # Parts flow through to finish(); each renderer processes them there.
        return title

    def render_row(self, label: str, value: str) -> str:
        # Same: pass the raw string through; each renderer formats in finish().
        return f"{label}::{value}"

    def finish(self, parts: list[str]) -> str:
        # Re-interpret parts: first part is the title, rest are "label::value" rows.
        # Let each sub-renderer reassemble from scratch.
        title = parts[0]
        rows = [p.split("::") for p in parts[1:]]

        outputs = []
        for renderer in self._renderers:
            sub_parts = [renderer.render_title(title)]
            for label, value in rows:
                sub_parts.append(renderer.render_row(label, value))
            outputs.append(renderer.finish(sub_parts))

        return "\n\n---\n\n".join(outputs)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    data = {"total": 14_200, "count": 47, "region": "UK"}

    print("=== SummaryReport + HtmlRenderer ===")
    html_report = SummaryReport(HtmlRenderer())
    result = html_report.generate(data)
    assert "<table>" in result
    assert "<h1>Summary</h1>" in result
    assert "14200" in result
    print(result)

    print("\n=== DetailedReport + CsvRenderer ===")
    csv_report = DetailedReport(CsvRenderer())
    result = csv_report.generate(data)
    assert "# Detailed Report" in result
    assert "total,14200" in result
    assert "region,UK" in result
    print(result)

    print("\n=== SummaryReport + MarkdownRenderer ===")
    md_report = SummaryReport(MarkdownRenderer())
    result = md_report.generate(data)
    assert "## Summary" in result
    assert "|---|---|" in result
    assert "| Total | 14200 |" in result
    print(result)

    print("\n=== Runtime switching ===")
    report = SummaryReport(HtmlRenderer())
    r1 = report.generate(data)
    assert "<table>" in r1

    report.switch_renderer(CsvRenderer())
    r2 = report.generate(data)
    assert "# Summary" in r2
    assert "<table>" not in r2

    report.switch_renderer(MarkdownRenderer())
    r3 = report.generate(data)
    assert "## Summary" in r3
    assert "|---|---|" in r3

    print("Runtime switching works correctly.")

    print("\n=== MultiRenderer ===")
    small_data = {"total": 100, "count": 5}
    multi = SummaryReport(MultiRenderer(HtmlRenderer(), CsvRenderer()))
    result = multi.generate(small_data)
    assert "<table>" in result
    assert "# Summary" in result
    assert "---" in result
    print(result)

    print("\nAll tests passed.")
