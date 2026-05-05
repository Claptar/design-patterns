---
layout: default
title: Exercise 1 - Factory Methods as Named Constructors
---

# Exercise 1: Factory Methods as Named Constructors

## Goal

Practice using factory methods when a class has several natural ways to create itself.

The focus of this exercise is not choosing between different classes. The focus is naming different construction paths clearly.

You will create a `Document` class that stores a normalized document:

```python
Document(title: str, body: str)
```

The final object should always store plain text in `body`, but callers may provide input in different formats.

---

## Task

Open `exercise1.py` and complete the `Document` class.

Implement these class methods:

```python
Document.from_plain_text(title, text)
Document.from_markdown(title, markdown)
Document.from_html(title, html)
```

Each method should return a `Document`.

---

## Requirements

### 1. `from_plain_text`

Should:

- strip leading/trailing whitespace from the title
- strip leading/trailing whitespace from the body
- return a `Document`

Example:

```python
doc = Document.from_plain_text(" Notes ", " Hello world ")

assert doc.title == "Notes"
assert doc.body == "Hello world"
```

### 2. `from_markdown`

Should:

- strip leading/trailing whitespace from the title
- remove simple Markdown heading markers such as `#`, `##`, and `###`
- remove simple bold markers `**`
- strip leading/trailing whitespace from the final body
- return a `Document`

Example:

```python
doc = Document.from_markdown(
    " Notes ",
    "# Heading\n\nThis is **important**.",
)

assert doc.title == "Notes"
assert "#" not in doc.body
assert "**" not in doc.body
assert "Heading" in doc.body
assert "important" in doc.body
```

You do not need to build a real Markdown parser. Keep the conversion simple.

### 3. `from_html`

Should:

- strip leading/trailing whitespace from the title
- remove simple HTML tags
- unescape basic HTML entities, such as `&amp;`
- strip leading/trailing whitespace from the final body
- return a `Document`

Example:

```python
doc = Document.from_html(
    " Notes ",
    "<h1>Heading</h1><p>Alice &amp; Bob</p>",
)

assert doc.title == "Notes"
assert "<h1>" not in doc.body
assert "Alice & Bob" in doc.body
```

---

## Test examples

The skeleton file includes a small `run_tests()` function. After completing the exercise, this command should pass:

```bash
python exercise1.py
```

The tests check behavior like this:

```python
def test_plain_text_document_creation():
    doc = Document.from_plain_text(" Notes ", " Hello world ")
    assert doc.title == "Notes"
    assert doc.body == "Hello world"


def test_markdown_document_creation():
    doc = Document.from_markdown(
        " Notes ",
        "# Heading\n\nThis is **important**.",
    )
    assert doc.title == "Notes"
    assert "#" not in doc.body
    assert "**" not in doc.body
    assert "Heading" in doc.body
    assert "important" in doc.body


def test_html_document_creation():
    doc = Document.from_html(
        " Notes ",
        "<h1>Heading</h1><p>Alice &amp; Bob</p>",
    )
    assert doc.title == "Notes"
    assert "<h1>" not in doc.body
    assert "Alice & Bob" in doc.body
```

You can add more tests if your implementation handles more Markdown or HTML cases.

---

## Questions to answer after completing it

1. Why is `Document.from_markdown(...)` clearer than `Document(...)`?
2. What does the method name communicate to the reader?
3. Would `Document.create(...)` be a good name here? Why or why not?
4. Should these methods be `@staticmethod` or `@classmethod`?

---

## Expected takeaway

Factory methods are useful when the same class has several meaningful ways to be created.

In this exercise:

```python
Document.from_plain_text(...)
Document.from_markdown(...)
Document.from_html(...)
```

all return a `Document`, but each method explains how the input should be interpreted.

---

[Back to Factory Methods as Named Constructors](factory_methods_named_constructors_note.md) · [Script](exercise1.py) · [Solution](solution1.md)
