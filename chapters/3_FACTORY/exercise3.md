---
layout: default
title: Exercise 3 - Factory Registry
---

# Exercise 3: Factory Registry

## Goal

Practice refactoring a simple factory from `if` / `elif` logic into a registry dictionary.

This exercise also shows an important design trade-off:

> A registry can make the factory easier to scan, but it does not completely solve the Open/Closed Principle problem.

---

## Starting point

In Exercise 2, the factory probably looked like this:

```python
if suffix == ".txt":
    return PlainTextDocumentImporter()

if suffix == ".md":
    return MarkdownDocumentImporter()

if suffix == ".html":
    return HtmlDocumentImporter()
```

This is fine for a few cases.

But as the number of supported file types grows, a dictionary can make the mapping clearer.

---

## Task

Open `exercise3.py` and complete the registry-based factory.

You need to implement:

```python
DocumentImporterFactory._importers
DocumentImporterFactory.create_for_file(path)
JsonDocumentImporter.import_document(path)
```

The factory should support:

```text
.txt   -> PlainTextDocumentImporter
.md    -> MarkdownDocumentImporter
.html  -> HtmlDocumentImporter
.json  -> JsonDocumentImporter
```

---

## Requirements

### 1. Registry dictionary

Create a class-level dictionary like this:

```python
_importers = {
    ".txt": PlainTextDocumentImporter,
    ".md": MarkdownDocumentImporter,
    ".html": HtmlDocumentImporter,
    ".json": JsonDocumentImporter,
}
```

The values should be classes, not instances.

That means the factory can instantiate the chosen class:

```python
return importer_class()
```

### 2. JSON importer

`JsonDocumentImporter` should read a JSON file shaped like this:

```json
{
  "title": "Notes",
  "body": "This came from JSON."
}
```

It should return a `Document`.

### 3. Unsupported files

Unsupported file types should raise `ValueError`.

---

## Test examples

The skeleton file includes temporary-file tests. After completing the exercise, this command should pass:

```bash
python exercise3.py
```

The tests check JSON support:

```python
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)

    json_path = root / "notes.json"
    json_path.write_text(
        json.dumps({"title": "JSON Notes", "body": "This came from JSON."}),
        encoding="utf-8",
    )

    importer = DocumentImporterFactory.create_for_file(str(json_path))
    assert isinstance(importer, JsonDocumentImporter)

    document = importer.import_document(str(json_path))
    assert document.title == "JSON Notes"
    assert document.body == "This came from JSON."
```

The registry should still support existing formats:

```python
md_path = root / "notes.md"
md_path.write_text("# Heading\n\nThis is **important**.", encoding="utf-8")

md_importer = DocumentImporterFactory.create_for_file(str(md_path))
assert isinstance(md_importer, MarkdownDocumentImporter)
assert "**" not in md_importer.import_document(str(md_path)).body
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

1. Is the registry easier to scan than the `if` / `elif` chain?
2. Does this fully satisfy the Open/Closed Principle?
3. What still needs to change when a new importer is added?
4. Why should the registry store classes instead of instances?

---

## Expected takeaway

A registry dictionary improves organization:

```python
_importers = {
    ".txt": PlainTextDocumentImporter,
    ".md": MarkdownDocumentImporter,
    ".html": HtmlDocumentImporter,
    ".json": JsonDocumentImporter,
}
```

But adding a new importer still requires modifying the registry.

So this is cleaner than a long conditional, but not a complete Open/Closed Principle solution.

---

[Back to Factories and the Open/Closed Principle](factories_and_open_closed_principle_note.md) · [Script](exercise3.py) · [Solution](solution3.md)
