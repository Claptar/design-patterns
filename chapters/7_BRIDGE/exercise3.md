---
layout: default
title: "Bridge Exercise 3: Runtime Switching & a Real Domain"
---

# Bridge Exercise 3: Runtime Switching & a Real Domain

## What's new

Exercises 1 and 2 showed the structural shape and the M×N payoff. This exercise adds two things that come up constantly in real code:

1. **Switching the implementor at runtime** — the bridge reference doesn't have to be fixed at construction. You can replace it later.
2. **A realistic domain** — you'll build the report rendering system from the pattern notes, then extend it.

---

## The domain: report rendering

A reporting system has two independent dimensions:

```
Report types:    SummaryReport, DetailedReport
Renderers:       HtmlRenderer, CsvRenderer, MarkdownRenderer
```

The `Report` abstraction generates structured content. The `Renderer` implementor decides how to format that content for output.

---

## Part A — Build the base system

### Implementor interface: `Renderer`

```python
class Renderer(ABC):
    @abstractmethod
    def render_title(self, title: str) -> str: ...

    @abstractmethod
    def render_row(self, label: str, value: str) -> str: ...

    @abstractmethod
    def finish(self, parts: list[str]) -> str: ...
```

### Concrete renderers

Implement `HtmlRenderer`, `CsvRenderer`, and `MarkdownRenderer`.

**`HtmlRenderer`:**
- `render_title` → `<h1>{title}</h1>`
- `render_row`   → `<tr><td>{label}</td><td>{value}</td></tr>`
- `finish`       → wraps everything in `<table>…</table>`

**`CsvRenderer`:**
- `render_title` → `# {title}`
- `render_row`   → `{label},{value}`
- `finish`       → joins parts with `\n`

**`MarkdownRenderer`:**
- `render_title` → `## {title}`
- `render_row`   → `| {label} | {value} |`
- `finish`       → adds a header separator row after the title line, then joins with `\n`

The markdown table format should look like:

```
## Monthly Summary
| label | value |
|---|---|
| Total | 14200 |
| Count | 47 |
```

Hint: the separator `|---|---|` needs to be inserted after the title row and before the data rows. Think about where in `finish()` that belongs.

### Abstraction base: `Report`

```python
class Report(ABC):
    def __init__(self, renderer: Renderer):
        self._renderer = renderer

    @abstractmethod
    def generate(self, data: dict) -> str: ...
```

### Concrete reports

**`SummaryReport`** renders only `total` and `count` from the data dict.

**`DetailedReport`** renders every key-value pair in the data dict.

---

## Part B — Runtime switching

Add a method to `Report` that allows swapping the renderer after construction:

```python
def switch_renderer(self, renderer: Renderer) -> None:
    ...
```

Then verify this works:

```python
data = {"total": 14_200, "count": 47, "region": "UK"}

report = SummaryReport(HtmlRenderer())
print(report.generate(data))

report.switch_renderer(CsvRenderer())
print(report.generate(data))

report.switch_renderer(MarkdownRenderer())
print(report.generate(data))
```

All three calls use the same `report` object and the same `data`. Only the output format changes.

---

## Part C — Add `MultiRenderer`

Add a new renderer that outputs to **multiple formats at once**:

```python
class MultiRenderer(Renderer):
    def __init__(self, *renderers: Renderer):
        ...
```

When `finish()` is called, it calls `finish()` on each of its child renderers and returns all outputs joined by `"\n\n---\n\n"`.

This is interesting because `MultiRenderer` is itself a `Renderer`, but it delegates to other `Renderer` objects. A renderer that composes other renderers — using the same bridge interface.

Expected output from `MultiRenderer(HtmlRenderer(), CsvRenderer())`:

```
<table><h1>Summary</h1><tr>...</tr></table>

---

# Summary
Total,14200
Count,47
```

---

## Skeleton

See `exercise3.py`.

---

## Things to think about

- `switch_renderer` is a one-liner. What does its simplicity tell you about where the coupling lives?
- `MultiRenderer` receives `Renderer` objects, not `Report` objects. What does that tell you about which hierarchy the composition belongs to?
- After Part C, how many classes would a non-Bridge design need to produce every report-type × renderer combination, including multi-output?

---

[Exercise 2](exercise2.md) · [Back to Bridge](bridge.md)
