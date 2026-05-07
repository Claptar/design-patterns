---
layout: default
title: "Bridge Exercise 3: Solution & Discussion"
---

# Bridge Exercise 3: Solution & Discussion

## The solution

### MarkdownRenderer.finish()

```python
def finish(self, parts: list[str]) -> str:
    return "\n".join([parts[0], "|---|---|", *parts[1:]])
```

The separator has to land between the title and the first data row. `parts[0]` is always the title (from `render_title`), so the insertion point is fixed. This is a small but important observation: the contract between `Report` and `Renderer` is that the first part is always the title. Both sides rely on that convention.

### switch_renderer()

```python
def switch_renderer(self, renderer: Renderer) -> None:
    self._renderer = renderer
```

One line. That's the whole method. This simplicity is telling: because the report only ever talks to the `Renderer` interface and never to a concrete class, swapping the concrete class at runtime requires changing exactly one reference. There's nothing else to update.

If the report had instead hard-coded `HtmlRenderer` anywhere inside its methods, every one of those hard-codings would need to change too.

### MultiRenderer

```python
class MultiRenderer(Renderer):
    def __init__(self, *renderers: Renderer):
        self._renderers = renderers

    def render_title(self, title: str) -> str:
        return title

    def render_row(self, label: str, value: str) -> str:
        return f"{label}::{value}"

    def finish(self, parts: list[str]) -> str:
        title = parts[0]
        rows = [p.split("::") for p in parts[1:]]

        outputs = []
        for renderer in self._renderers:
            sub_parts = [renderer.render_title(title)]
            for label, value in rows:
                sub_parts.append(renderer.render_row(label, value))
            outputs.append(renderer.finish(sub_parts))

        return "\n\n---\n\n".join(outputs)
```

---

## Discussion

### Why MultiRenderer belongs in the implementor hierarchy

You might have considered putting multi-output behavior on the `Report` side:

```python
class MultiFormatReport(Report):
    def __init__(self, renderers: list[Renderer]):
        ...
```

That would also work, but it conflates two different concerns: what the report contains (the abstraction's job) and how many formats it outputs (the implementor's job). By putting `MultiRenderer` in the implementor hierarchy, any report type automatically gets multi-output for free:

```python
SummaryReport(MultiRenderer(HtmlRenderer(), CsvRenderer()))
DetailedReport(MultiRenderer(HtmlRenderer(), MarkdownRenderer()))
```

No new report classes needed.

### The intermediate encoding in render_title / render_row

`MultiRenderer.render_title` and `render_row` return raw strings that `finish()` later re-interprets. This is a design tradeoff worth noting.

The cleaner design would give each sub-renderer its own stream of calls — but the `Renderer` interface as defined doesn't support that. Each renderer gets one `finish()` call with a flat list of parts.

The solution works around this by encoding the raw data into the parts list (using `::` as a separator) and decoding it in `finish()`. This is a valid approach for this exercise, but in production code you might instead redesign the interface to support streaming parts per-renderer, or pass a richer data structure instead of strings.

This is a good example of a real constraint the pattern surfaces: the interface between abstraction and implementor must be rich enough to support all the implementors you plan to write. If `MultiRenderer` was a requirement from the start, the `Renderer` interface might have been designed differently.

### The count question from the exercise

After Part C, the non-Bridge class count for all combinations:

```
Report types: SummaryReport, DetailedReport
Renderers:    HtmlRenderer, CsvRenderer, MarkdownRenderer, MultiRenderer(Html+Csv),
              MultiRenderer(Html+Md), MultiRenderer(Csv+Md), MultiRenderer(all three)
```

That's 2 report types × 7 renderer combinations = **14 classes**, and we haven't even counted multi-renderer combinations with four or more renderers. With Bridge: 2 + 4 = **6 classes**, and `MultiRenderer` itself handles all combinations without new classes.

---

## Summary of the three exercises

| Exercise | What you learned |
|---|---|
| 1 | The basic Bridge shape: two hierarchies, one reference |
| 2 | The M×N payoff: adding to one side doesn't touch the other |
| 3 | Runtime switching is free; the implementor side can compose |

The pattern's core discipline is always the same:

> The abstraction only speaks to the implementor interface. Never to a concrete class.

Everything else — the M×N savings, runtime switching, `MultiRenderer` — follows from that one rule.

---

[Exercise 2](exercise2.md) · [Back to Bridge](bridge.md)
