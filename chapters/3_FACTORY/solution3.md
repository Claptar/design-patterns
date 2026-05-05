---
layout: default
title: Solution 3 - Factory Registry
---

# Solution 3: Factory Registry

## Completed idea

The factory no longer uses a long `if` / `elif` chain.

Instead, it stores the mapping between file extensions and importer classes in one dictionary.

```python
_importers = {
    ".txt": PlainTextDocumentImporter,
    ".md": MarkdownDocumentImporter,
    ".html": HtmlDocumentImporter,
    ".json": JsonDocumentImporter,
}
```

This makes the decision table easier to see.

---

## Solution

```python
class DocumentImporterFactory:
    _importers = {
        ".txt": PlainTextDocumentImporter,
        ".md": MarkdownDocumentImporter,
        ".html": HtmlDocumentImporter,
        ".json": JsonDocumentImporter,
    }

    @classmethod
    def create_for_file(cls, path: str) -> DocumentImporter:
        suffix = Path(path).suffix.lower()

        try:
            importer_class = cls._importers[suffix]
        except KeyError:
            raise ValueError(f"Unsupported document type: {path}") from None

        return importer_class()
```

---

## Why store classes instead of instances?

The registry stores classes:

```python
".md": MarkdownDocumentImporter
```

not instances:

```python
".md": MarkdownDocumentImporter()
```

This lets the factory create a fresh importer each time:

```python
return importer_class()
```

That is useful if importers later have per-instance state.

For stateless importers, storing instances could work, but storing classes is a good default for this exercise.

---

## Does this satisfy the Open/Closed Principle?

Not completely.

If we add XML support, we still need to modify the registry:

```python
_importers = {
    ".txt": PlainTextDocumentImporter,
    ".md": MarkdownDocumentImporter,
    ".html": HtmlDocumentImporter,
    ".json": JsonDocumentImporter,
    ".xml": XmlDocumentImporter,
}
```

So the factory is still not fully closed for modification.

However, the registry is still an improvement over a long conditional because the mapping is explicit and easy to scan.

---

## Discussion

The registry version is a middle step.

It improves this:

```python
if suffix == ".txt":
    return PlainTextDocumentImporter()
if suffix == ".md":
    return MarkdownDocumentImporter()
if suffix == ".html":
    return HtmlDocumentImporter()
```

into this:

```python
_importers = {
    ".txt": PlainTextDocumentImporter,
    ".md": MarkdownDocumentImporter,
    ".html": HtmlDocumentImporter,
}
```

The design is still centralized.

That is often good enough for a small or stable application.

If the list of importers changes frequently, then a registration-based approach may be better.

---

## Final takeaway

A registry dictionary makes a factory easier to maintain and read, but it does not completely remove the need to modify the factory when new implementations are added.

It is cleaner organization, not full Open/Closed Principle compliance.

---

[Back to exercise](exercise3.md) · [Solution script](exercise3_solution.py)
