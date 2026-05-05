---
layout: default
title: Solution 2 - Simple Factory
---

# Solution 2: Simple Factory

## Completed idea

The `Document` class still has named constructors:

```python
Document.from_plain_text(...)
Document.from_markdown(...)
Document.from_html(...)
```

But now we also have multiple importer classes:

```python
PlainTextDocumentImporter
MarkdownDocumentImporter
HtmlDocumentImporter
```

The factory chooses which importer to create based on the file extension.

---

## Solution

```python
class DocumentImporterFactory:
    @staticmethod
    def create_for_file(path: str) -> DocumentImporter:
        suffix = Path(path).suffix.lower()

        if suffix == ".txt":
            return PlainTextDocumentImporter()

        if suffix == ".md":
            return MarkdownDocumentImporter()

        if suffix == ".html":
            return HtmlDocumentImporter()

        raise ValueError(f"Unsupported document type: {path}")
```

Usage:

```python
importer = DocumentImporterFactory.create_for_file("notes.md")
document = importer.import_document("notes.md")
```

---

## Why this is a factory

The caller knows the situation:

```python
path = "notes.md"
```

But the caller should not need to know the concrete importer class.

The caller wants to say:

```text
Give me the correct importer for this file.
```

The factory decides:

```text
.md means MarkdownDocumentImporter.
```

That is different from a factory method like:

```python
Document.from_markdown(...)
```

`Document.from_markdown(...)` creates a `Document` from Markdown.

`DocumentImporterFactory.create_for_file(...)` chooses which importer object to create.

---

## Why not repeat the conditional?

Without the factory, this logic may appear in many places:

```python
if path.endswith(".txt"):
    importer = PlainTextDocumentImporter()
elif path.endswith(".md"):
    importer = MarkdownDocumentImporter()
elif path.endswith(".html"):
    importer = HtmlDocumentImporter()
```

That creates duplication.

If we add a new file type, every duplicated conditional may need to change.

With the factory, the decision has one home.

---

## Discussion

This simple factory still uses `if` / `elif` internally.

That is not automatically bad.

The main improvement is that the decision is centralized.

The rest of the application can work with the common interface:

```python
importer.import_document(path)
```

It does not need to know which concrete importer was created.

---

## Final takeaway

A simple factory is useful when object creation involves a runtime decision.

In this exercise, the runtime decision is:

```text
Which importer should handle this file extension?
```

---

[Back to exercise](exercise2.md) · [Solution script](exercise2_solution.py)
