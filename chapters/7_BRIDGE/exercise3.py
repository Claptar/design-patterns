"""
Bridge Exercise 3: Runtime Switching & a Real Domain

Parts:
  A  -- Build HtmlRenderer, CsvRenderer, MarkdownRenderer,
        SummaryReport, DetailedReport
  B  -- Add switch_renderer() to Report
  C  -- Add MultiRenderer
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
    def finish(self, parts: list[str]) -> str:
        """Assemble the collected parts into a final string."""
        ...


# ---------------------------------------------------------------------------
# Part A: Concrete renderers
# ---------------------------------------------------------------------------

class HtmlRenderer(Renderer):
    def render_title(self, title: str) -> str:
        # TODO: return "<h1>{title}</h1>"
        pass

    def render_row(self, label: str, value: str) -> str:
        # TODO: return "<tr><td>{label}</td><td>{value}</td></tr>"
        pass

    def finish(self, parts: list[str]) -> str:
        # TODO: return "<table>" + "".join(parts) + "</table>"
        pass


class CsvRenderer(Renderer):
    def render_title(self, title: str) -> str:
        # TODO: return "# {title}"
        pass

    def render_row(self, label: str, value: str) -> str:
        # TODO: return "{label},{value}"
        pass

    def finish(self, parts: list[str]) -> str:
        # TODO: join parts with "\n"
        pass


class MarkdownRenderer(Renderer):
    def render_title(self, title: str) -> str:
        # TODO: return "## {title}"
        pass

    def render_row(self, label: str, value: str) -> str:
        # TODO: return "| {label} | {value} |"
        pass

    def finish(self, parts: list[str]) -> str:
        # TODO: insert "|---|---|" after the title row (index 0),
        #       then join all parts with "\n"
        #
        # Expected shape:
        #   parts[0]  = "## Summary"
        #   separator = "|---|---|"
        #   parts[1:] = row strings
        #   result    = "\n".join([parts[0], "|---|---|", *parts[1:]])
        pass


# ---------------------------------------------------------------------------
# Part A: Abstraction base and concrete reports
# ---------------------------------------------------------------------------

class Report(ABC):
    def __init__(self, renderer: Renderer):
        # TODO: store renderer as self._renderer
        pass

    @abstractmethod
    def generate(self, data: dict) -> str: ...

    # Part B: add switch_renderer here
    def switch_renderer(self, renderer: Renderer) -> None:
        # TODO: replace self._renderer with the new renderer
        pass


class SummaryReport(Report):
    def generate(self, data: dict) -> str:
        # TODO:
        #   parts = [render_title("Summary")]
        #   append render_row("Total", str(data.get("total", 0)))
        #   append render_row("Count", str(data.get("count", 0)))
        #   return finish(parts)
        pass


class DetailedReport(Report):
    def generate(self, data: dict) -> str:
        # TODO:
        #   parts = [render_title("Detailed Report")]
        #   for each key, value in data.items():
        #       append render_row(key, str(value))
        #   return finish(parts)
        pass


# ---------------------------------------------------------------------------
# Part C: MultiRenderer
# ---------------------------------------------------------------------------

class MultiRenderer(Renderer):
    """Delegates to multiple renderers and concatenates their output."""

    def __init__(self, *renderers: Renderer):
        # TODO: store renderers as self._renderers
        pass

    def render_title(self, title: str) -> str:
        # TODO: call render_title on each renderer, return as list
        #       (store results; they will be passed to finish later)
        #       Hint: since finish() receives a flat list of parts,
        #       you need each renderer to collect its own parts.
        #       One approach: each method collects into self._buffers[i].
        #
        # Simpler approach used in the solution:
        #   store the title/row calls into per-renderer buffers,
        #   then assemble in finish().
        #
        # For now, return "" and implement the logic in finish() instead.
        pass

    def render_row(self, label: str, value: str) -> str:
        # TODO: same as above — return "" and handle in finish()
        pass

    def finish(self, parts: list[str]) -> str:
        # TODO: call generate-equivalent logic on each sub-renderer.
        #
        # Hint: the challenge here is that finish() receives `parts` —
        # a list of strings produced by render_title + render_row calls
        # from the Report. But those strings are plain strings, not tagged
        # by renderer. So the cleanest approach is:
        #
        #   for each sub-renderer r:
        #       call r.finish(parts)   <-- each renderer formats the same parts
        #   join the results with "\n\n---\n\n"
        #
        # This works because render_title and render_row just produce strings,
        # and each renderer's finish() reassembles them independently.
        pass


# ---------------------------------------------------------------------------
# Tests — do not edit below this line
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    data = {"total": 14_200, "count": 47, "region": "UK"}

    # Part A: basic rendering
    print("=== SummaryReport + HtmlRenderer ===")
    html_report = SummaryReport(HtmlRenderer())
    result = html_report.generate(data)
    assert "<table>" in result, "Expected <table>"
    assert "<h1>Summary</h1>" in result, "Expected <h1>Summary</h1>"
    assert "14200" in result, "Expected total value"
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

    # Part B: runtime switching
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

    # Part C: MultiRenderer
    print("\n=== MultiRenderer ===")
    small_data = {"total": 100, "count": 5}
    multi = SummaryReport(MultiRenderer(HtmlRenderer(), CsvRenderer()))
    result = multi.generate(small_data)
    assert "<table>" in result, "Expected HTML output in multi"
    assert "# Summary" in result, "Expected CSV output in multi"
    assert "---" in result, "Expected separator between outputs"
    print(result)

    print("\nAll tests passed.")
