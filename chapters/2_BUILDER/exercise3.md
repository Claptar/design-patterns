---
layout: default
title: Exercise 3: Builder Inheritance
---

# Exercise 3: Build an inheritance-based message builder

In the previous exercise, you split a builder into **facets** so each part of the object had its own focused builder.

In this exercise, you will practice **builder inheritance**.

Builder inheritance is useful when the objects being built also use inheritance.

For example:

```text
Message
└── EmailMessage
```

The child builder should reuse the parent builder's fluent methods and add child-specific methods.

---

## Final objects

Do not change these dataclasses.

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Message:
    recipient: str
    subject: str
    priority: str


@dataclass(frozen=True)
class EmailMessage(Message):
    html_body: str
    cc: tuple[str, ...] = field(default_factory=tuple)
    bcc: tuple[str, ...] = field(default_factory=tuple)
```

`EmailMessage` extends `Message` by adding:

```text
html_body
cc
bcc
```

---

## Goal

Implement two builders:

```text
MessageBuilder
EmailMessageBuilder
```

`EmailMessageBuilder` should inherit from `MessageBuilder`.

The parent builder should provide common message-building methods.

The child builder should reuse those methods and add email-specific methods.

---

## Required fluent API

This should work:

```python
message = (
    MessageBuilder()
    .to("alice@example.com")
    .subject("System alert")
    .high_priority()
    .build()
)
```

This should also work:

```python
email = (
    EmailMessageBuilder()
    .to("alice@example.com")
    .subject("Your invoice")
    .normal_priority()
    .html("<p>Thanks for your purchase.</p>")
    .cc("accounts@example.com")
    .bcc("audit@example.com")
    .build()
)
```

The important part is this:

```python
EmailMessageBuilder().to(...).subject(...).html(...)
```

The `.to(...)` and `.subject(...)` methods are inherited from `MessageBuilder`, but chaining should still continue with `.html(...)`, which belongs only to `EmailMessageBuilder`.

---

## Required classes

Implement:

```text
MessageBuilder
EmailMessageBuilder
```

You may also add helper methods if useful.

---

## MessageBuilder requirements

`MessageBuilder` should collect:

| Field | Default |
|---|---|
| `recipient` | required |
| `subject` | required |
| `priority` | `"normal"` |

It should support these methods:

```text
.to(recipient)
.subject(subject)
.low_priority()
.normal_priority()
.high_priority()
.build()
```

All fluent methods should return `self`.

`build()` should return a `Message`.

---

## EmailMessageBuilder requirements

`EmailMessageBuilder` should inherit from `MessageBuilder`.

It should reuse:

```text
.to(...)
.subject(...)
.low_priority()
.normal_priority()
.high_priority()
```

It should add:

```text
.html(html_body)
.cc(recipient)
.bcc(recipient)
.build()
```

All fluent methods should return `self`.

`build()` should return an `EmailMessage`.

---

## Defaults

Use these defaults:

| Field | Default |
|---|---|
| `priority` | `"normal"` |
| `cc` | empty tuple |
| `bcc` | empty tuple |

---

## Validation rules

The final `build()` method should validate the completed object.

Rules for `MessageBuilder.build()`:

- `recipient` is required.
- `subject` is required.
- `priority` must be `"low"`, `"normal"`, or `"high"`.

Additional rules for `EmailMessageBuilder.build()`:

- `html_body` is required.
- Every `cc` recipient must be non-empty.
- Every `bcc` recipient must be non-empty.

---

## Normalization rules

Apply these normalization rules:

- `recipient` should be stripped and lowercased.
- `cc` recipients should be stripped and lowercased.
- `bcc` recipients should be stripped and lowercased.
- `subject` should be stripped.
- `html_body` should be stripped.

---

## Failure examples

This should fail because recipient is missing:

```python
message = (
    MessageBuilder()
    .subject("Hello")
    .build()
)
```

This should fail because subject is missing:

```python
message = (
    MessageBuilder()
    .to("alice@example.com")
    .build()
)
```

This should fail because email body is missing:

```python
email = (
    EmailMessageBuilder()
    .to("alice@example.com")
    .subject("Hello")
    .build()
)
```

This should fail because `cc` is blank:

```python
email = (
    EmailMessageBuilder()
    .to("alice@example.com")
    .subject("Hello")
    .html("<p>Hello</p>")
    .cc("   ")
    .build()
)
```

---

## Starter skeleton

The starter code is also available in `exercise3.py`.

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self


@dataclass(frozen=True)
class Message:
    recipient: str
    subject: str
    priority: str


@dataclass(frozen=True)
class EmailMessage(Message):
    html_body: str
    cc: tuple[str, ...] = field(default_factory=tuple)
    bcc: tuple[str, ...] = field(default_factory=tuple)


class MessageBuilder:
    def __init__(self):
        self._recipient = None
        self._subject = None
        self._priority = "normal"

    def to(self, recipient: str) -> Self:
        # TODO
        return self

    def subject(self, subject: str) -> Self:
        # TODO
        return self

    def low_priority(self) -> Self:
        # TODO
        return self

    def normal_priority(self) -> Self:
        # TODO
        return self

    def high_priority(self) -> Self:
        # TODO
        return self

    def build(self) -> Message:
        # TODO: validate and return Message(...)
        pass


class EmailMessageBuilder(MessageBuilder):
    def __init__(self):
        super().__init__()
        self._html_body = None
        self._cc = []
        self._bcc = []

    def html(self, html_body: str) -> Self:
        # TODO
        return self

    def cc(self, recipient: str) -> Self:
        # TODO
        return self

    def bcc(self, recipient: str) -> Self:
        # TODO
        return self

    def build(self) -> EmailMessage:
        # TODO: validate common Message fields
        # TODO: validate EmailMessage-specific fields
        # TODO: return EmailMessage(...)
        pass
```

---

## Hint

In Python, returning `self` is usually enough for fluent inheritance to work at runtime.

For type hints, use `Self`:

```python
from typing import Self
```

Then inherited methods like this:

```python
def to(self, recipient: str) -> Self:
    ...
    return self
```

will be understood by type checkers as returning the concrete builder type.

So if `EmailMessageBuilder` inherits `.to(...)`, the chain can continue with email-specific methods:

```python
EmailMessageBuilder().to("alice@example.com").html("<p>Hello</p>")
```

---

[Back to Builder Inheritance](builder_inheritance.md) · [Script](exercise3.py) · [Solution](solution3.md)
