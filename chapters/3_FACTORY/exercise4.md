---
layout: default
title: Exercise 4 - Registration-Based Factory
---

# Exercise 4: Registration-Based Factory

## Goal

Practice making a factory more extensible through registration.

In Exercise 3, the registry dictionary made the factory easier to scan:

```python
_importers = {
    ".txt": PlainTextDocumentImporter,
    ".md": MarkdownDocumentImporter,
    ".html": HtmlDocumentImporter,
    ".json": JsonDocumentImporter,
}
```

But adding a new importer still required editing the factory's registry.

In this exercise, you will let importer classes register themselves.

---

## Task

Open `exercise4.py` and complete `DocumentImporterFactory` so that this works:

```python
@DocumentImporterFactory.register(".md")
class MarkdownDocumentImporter(DocumentImporter):
    ...
```

The factory should support:

```text
.txt
.md
.html
.json
```

using decorator-based registration.

---

## Requirements

### 1. Implement `register`

Complete this method:

```python
@classmethod
def register(cls, extension: str):
    ...
```

It should return a decorator.

The decorator should:

- store the importer class in `cls._importers`
- return the importer class unchanged

Expected usage:

```python
@DocumentImporterFactory.register(".txt")
class PlainTextDocumentImporter(DocumentImporter):
    ...
```

### 2. Implement `create_for_file`

Complete:

```python
DocumentImporterFactory.create_for_file(path)
```

It should:

- inspect the file extension
- look up the importer class in `_importers`
- instantiate and return the importer
- raise `ValueError` for unsupported file types

### 3. Add a new importer without editing the factory class

Add support for `.json` by registering `JsonDocumentImporter`.

The factory class itself should not need a hardcoded `.json` branch.

---

## Test examples

The skeleton file includes temporary-file tests. After completing the exercise, this command should pass:

```bash
python exercise4.py
```

The tests check that decorator registration works:

```python
md_path = root / "notes.md"
md_path.write_text("# Heading\n\nThis is **important**.", encoding="utf-8")

md_importer = DocumentImporterFactory.create_for_file(str(md_path))
assert isinstance(md_importer, MarkdownDocumentImporter)
assert "**" not in md_importer.import_document(str(md_path)).body
```

They also check the `.json` importer:

```python
json_path = root / "notes.json"
json_path.write_text(
    json.dumps({"title": "JSON Notes", "body": "This came from JSON."}),
    encoding="utf-8",
)

json_importer = DocumentImporterFactory.create_for_file(str(json_path))
assert isinstance(json_importer, JsonDocumentImporter)
assert json_importer.import_document(str(json_path)).title == "JSON Notes"
```

The registry should contain the registered extensions:

```python
assert ".txt" in DocumentImporterFactory._importers
assert ".md" in DocumentImporterFactory._importers
assert ".html" in DocumentImporterFactory._importers
assert ".json" in DocumentImporterFactory._importers
```

Unsupported files should raise `ValueError`:

```python
try:
    DocumentImporterFactory.create_for_file("notes.pdf")
except ValueError:
    pass
else:
    raise AssertionError("Unsupported file type should raise ValueError")
```

---

## Questions to answer after completing it

1. How does registration improve the Open/Closed Principle compared with Exercise 3?
2. What new complexity does registration introduce?
3. Why does the decorator return the importer class?
4. What happens if the module containing a registered importer is never imported?

---

## Expected takeaway

Decorator-based registration lets new classes attach themselves to the factory without editing the factory class.

This is more extensible than a hardcoded registry, but it adds indirection.

The key trade-off is:

```text
More extensibility often means less obvious control flow.
```

---

[Back to Factories and the Open/Closed Principle](factories_and_open_closed_principle_note.md) · [Script](exercise4.py) · [Solution](solution4.md)
