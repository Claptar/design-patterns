---
layout: default
title: Exercise 2 - Simple Factory
---

# Exercise 2: Simple Factory

## Goal

Practice creating a simple factory that chooses between several related concrete classes.

In Exercise 1, `Document.from_markdown(...)` and `Document.from_html(...)` were factory methods because `Document` was creating itself from different input representations.

Now the problem changes.

Users upload files:

```text
notes.txt
notes.md
notes.html
```

The application should choose the correct importer based on the file extension.

This is no longer just one class creating itself. The program must choose between several importer classes.

---

## Task

Open `exercise2.py` and complete the importer system.

You need to implement:

```python
PlainTextDocumentImporter.import_document(path)
MarkdownDocumentImporter.import_document(path)
HtmlDocumentImporter.import_document(path)
DocumentImporterFactory.create_for_file(path)
```

---

## Requirements

### 1. Importer classes

Each importer should expose the same method:

```python
import_document(path: str) -> Document
```

Each importer should read the file and return a `Document`.

Use the filename stem as the title.

For example:

```text
notes.md -> title "notes"
```

The importer should delegate conversion to the appropriate `Document` factory method:

```python
Document.from_plain_text(...)
Document.from_markdown(...)
Document.from_html(...)
```

### 2. Factory

Implement:

```python
DocumentImporterFactory.create_for_file(path)
```

It should return:

```text
.txt   -> PlainTextDocumentImporter
.md    -> MarkdownDocumentImporter
.html  -> HtmlDocumentImporter
```

For unsupported file types, raise `ValueError`.

---

## Example usage

```python
importer = DocumentImporterFactory.create_for_file("notes.md")
document = importer.import_document("notes.md")
```

The caller should not need to know whether the concrete importer is `PlainTextDocumentImporter`, `MarkdownDocumentImporter`, or `HtmlDocumentImporter`.

---

## Test examples

The skeleton file includes temporary-file tests. After completing the exercise, this command should pass:

```bash
python exercise2.py
```

The tests check behavior like this:

```python
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)

    txt_path = root / "notes.txt"
    txt_path.write_text(" Hello plain text ", encoding="utf-8")

    txt_importer = DocumentImporterFactory.create_for_file(str(txt_path))
    assert isinstance(txt_importer, PlainTextDocumentImporter)

    document = txt_importer.import_document(str(txt_path))
    assert document.title == "notes"
    assert document.body == "Hello plain text"
```

Markdown and HTML should work too:

```python
md_path = root / "notes.md"
md_path.write_text("# Heading\n\nThis is **important**.", encoding="utf-8")

md_importer = DocumentImporterFactory.create_for_file(str(md_path))
assert isinstance(md_importer, MarkdownDocumentImporter)
assert "**" not in md_importer.import_document(str(md_path)).body

html_path = root / "notes.html"
html_path.write_text("<h1>Heading</h1><p>Alice &amp; Bob</p>", encoding="utf-8")

html_importer = DocumentImporterFactory.create_for_file(str(html_path))
assert isinstance(html_importer, HtmlDocumentImporter)
assert "Alice & Bob" in html_importer.import_document(str(html_path)).body
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

1. Why does this need a separate factory instead of only `Document.from_markdown(...)`?
2. What decision is the factory making?
3. What do all importer classes have in common?
4. What would happen if the `if` / `elif` logic were repeated across the application?

---

## Expected takeaway

Use a factory when the program needs to choose between several related concrete classes.

Here, the factory answers:

```text
Given this file path, which importer class should be created?
```

---

[Back to Factories](factory.md) · [Script](exercise2.py) · [Solution](solution2.md)
