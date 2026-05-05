---
layout: default
title: Solution 1 - Factory Methods as Named Constructors
---

# Solution 1: Factory Methods as Named Constructors

## Completed idea

The `Document` class stores one normalized representation:

```python
Document(title: str, body: str)
```

But the input can arrive in several different formats:

```python
Document.from_plain_text(...)
Document.from_markdown(...)
Document.from_html(...)
```

These are factory methods used as named constructors.

They do not choose between many concrete classes. They create the same class from different kinds of input.

---

## Solution

```python
from dataclasses import dataclass
from html import unescape
import re


@dataclass(frozen=True)
class Document:
    title: str
    body: str

    @classmethod
    def from_plain_text(cls, title: str, text: str):
        return cls(
            title=title.strip(),
            body=text.strip(),
        )

    @classmethod
    def from_markdown(cls, title: str, markdown: str):
        body = markdown.strip()
        body = re.sub(r"^#{1,6}\s*", "", body, flags=re.MULTILINE)
        body = body.replace("**", "")

        return cls(
            title=title.strip(),
            body=body.strip(),
        )

    @classmethod
    def from_html(cls, title: str, html: str):
        body = re.sub(r"<[^>]+>", " ", html)
        body = unescape(body)
        body = " ".join(body.split())

        return cls(
            title=title.strip(),
            body=body.strip(),
        )
```

---

## Why this is a good factory method example

The constructor is simple:

```python
Document(title, body)
```

But if callers use it directly, they need to know that `body` should already be plain text.

This would be unclear:

```python
doc = Document("Notes", "# Heading

This is **important**.")
```

Should the `Document` store Markdown? Should it convert Markdown? Has conversion already happened?

This is clearer:

```python
doc = Document.from_markdown(
    "Notes",
    "# Heading

This is **important**."
)
```

The method name says:

```text
This input is Markdown. Convert it into the normalized Document representation.
```

The same applies to HTML:

```python
doc = Document.from_html("Notes", "<p>Hello</p>")
```

The method name tells the reader how the input is being interpreted.

---

## Why not `Document.create(...)`?

This would be weaker:

```python
doc = Document.create(data)
```

The name `create` does not tell us what kind of data is being passed.

These names are better:

```python
Document.from_plain_text(...)
Document.from_markdown(...)
Document.from_html(...)
```

The value of a factory method as a named constructor is in the name.

A good name explains the construction path.

---

## Why `@classmethod`?

These methods are written as class methods:

```python
@classmethod
def from_html(cls, title: str, html: str):
    return cls(...)
```

Using `cls` means subclasses can inherit the factory method more naturally.

A static method would usually hardcode the class:

```python
@staticmethod
def from_html(title: str, html: str):
    return Document(...)
```

That works, but it is less flexible.

For named constructors in Python, `@classmethod` is usually the better default.

---

## Discussion

This exercise is about factory methods, not factories.

There is no separate `DocumentFactory` here because we are not choosing between many concrete classes.

We are just giving `Document` several clear ways to create itself.

The question being answered is:

```text
How should this Document be created from this kind of input?
```

not:

```text
Which class should be created?
```

---

## Final takeaway

Use factory methods as named constructors when a direct constructor call would hide the meaning of the input.

```python
Document.from_markdown(...)
```

is clearer than:

```python
Document(...)
```

when the important thing is that the input must be interpreted as Markdown before becoming a normalized `Document`.

---

[Back to exercise](exercise1.md) · [Solution script](exercise1_solution.py)
