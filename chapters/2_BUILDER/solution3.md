---
layout: default
title: Exercise 3 Solution: Builder Inheritance with Cooperative Validation
---

# Exercise 3 Solution: Builder Inheritance with Cooperative Validation

This solution uses **builder inheritance** for a small hierarchy:

```text
Message
└── EmailMessage
```

And the builders mirror that hierarchy:

```text
MessageBuilder
└── EmailMessageBuilder
```

The important goal is that `EmailMessageBuilder` reuses the common message-building methods from `MessageBuilder`:

```python
.to(...)
.subject(...)
.low_priority()
.normal_priority()
.high_priority()
```

while adding email-specific methods:

```python
.html(...)
.cc(...)
.bcc(...)
```

The final usage should work like this:

```python
email = (
    EmailMessageBuilder()
    .to("ALICE@EXAMPLE.COM")
    .subject(" Your invoice ")
    .high_priority()
    .html(" <p>Thanks for your purchase.</p> ")
    .cc("ACCOUNTS@EXAMPLE.COM")
    .bcc("AUDIT@EXAMPLE.COM")
    .build()
)
```

---

## 1. Final objects

The final objects are immutable dataclasses.

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

`EmailMessage` inherits the common message fields from `Message`, then adds email-specific fields.

---

## 2. Base builder

`MessageBuilder` owns the common construction state:

```python
class MessageBuilder:
    VALID_PRIORITIES = {"low", "normal", "high"}

    def __init__(self):
        self._recipient = None
        self._subject = None
        self._priority = "normal"
```

It provides common fluent methods:

```python
    def to(self, recipient: str) -> Self:
        self._recipient = recipient.strip().lower()
        return self

    def subject(self, subject: str) -> Self:
        self._subject = subject.strip()
        return self

    def low_priority(self) -> Self:
        self._priority = "low"
        return self

    def normal_priority(self) -> Self:
        self._priority = "normal"
        return self

    def high_priority(self) -> Self:
        self._priority = "high"
        return self
```

The return type is `Self`, so when these methods are inherited by `EmailMessageBuilder`, fluent chaining still returns the subclass builder.

That means this works:

```python
EmailMessageBuilder().to("alice@example.com").html("<p>Hello</p>")
```

After `.to(...)`, the chain is still an `EmailMessageBuilder`.

---

## 3. Cooperative validation

Instead of using a method like `_validate_common_fields()`, this solution uses a cooperative validation method:

```python
    def validate(self) -> None:
        ...
```

The base builder validates base fields:

```python
    def validate(self) -> None:
        if not self._recipient:
            raise ValueError("Recipient is required")

        if not self._subject:
            raise ValueError("Subject is required")

        if self._priority not in self.VALID_PRIORITIES:
            raise ValueError("Priority must be 'low', 'normal', or 'high'")
```

Then `build()` calls `validate()`:

```python
    def build(self) -> Message:
        self.validate()
        return Message(
            recipient=self._recipient,
            subject=self._subject,
            priority=self._priority,
        )
```

This approach scales better if there are more inheritance layers.

Each subclass can do this:

```python
def validate(self) -> None:
    super().validate()
    # validate fields introduced by this subclass
```

So validation follows the inheritance chain naturally.

---

## 4. Subclass builder

`EmailMessageBuilder` inherits all common message-building methods from `MessageBuilder`, then adds email-specific state:

```python
class EmailMessageBuilder(MessageBuilder):
    def __init__(self):
        super().__init__()
        self._html_body = None
        self._cc = []
        self._bcc = []
```

It also adds email-specific fluent methods:

```python
    def html(self, html_body: str) -> Self:
        self._html_body = html_body.strip()
        return self

    def cc(self, recipient: str) -> Self:
        recipient = recipient.strip().lower()
        if not recipient:
            raise ValueError("CC recipient cannot be blank")
        self._cc.append(recipient)
        return self

    def bcc(self, recipient: str) -> Self:
        recipient = recipient.strip().lower()
        if not recipient:
            raise ValueError("BCC recipient cannot be blank")
        self._bcc.append(recipient)
        return self
```

---

## 5. Subclass validation

The subclass extends validation by calling `super().validate()` first:

```python
    def validate(self) -> None:
        super().validate()

        if not self._html_body:
            raise ValueError("HTML body is required")
```

This is the key part of the solution.

`MessageBuilder` validates common fields:

```text
recipient
subject
priority
```

`EmailMessageBuilder` validates email-specific fields:

```text
html_body
```

If another subclass were added later, it could follow the same pattern.

---

## 6. Subclass build method

The subclass `build()` method calls `self.validate()` once, then creates the final `EmailMessage` directly:

```python
    def build(self) -> EmailMessage:
        self.validate()
        return EmailMessage(
            recipient=self._recipient,
            subject=self._subject,
            priority=self._priority,
            html_body=self._html_body,
            cc=tuple(self._cc),
            bcc=tuple(self._bcc),
        )
```

This avoids creating a temporary base `Message` just to reuse validation.

---

## 7. Complete usage

```python
email = (
    EmailMessageBuilder()
    .to("ALICE@EXAMPLE.COM")
    .subject(" Your invoice ")
    .high_priority()
    .html(" <p>Thanks for your purchase.</p> ")
    .cc("ACCOUNTS@EXAMPLE.COM")
    .bcc("AUDIT@EXAMPLE.COM")
    .build()
)
```

The result is:

```python
EmailMessage(
    recipient="alice@example.com",
    subject="Your invoice",
    priority="high",
    html_body="<p>Thanks for your purchase.</p>",
    cc=("accounts@example.com",),
    bcc=("audit@example.com",),
)
```

---

## 8. Why this solution is good

This solution demonstrates builder inheritance clearly:

| Part | Responsibility |
|---|---|
| `MessageBuilder` | Common message fields and validation. |
| `EmailMessageBuilder` | Email-specific fields and validation. |
| `Self` return type | Preserves fluent chaining through inherited builder methods. |
| `validate()` | Lets each inheritance layer validate its own fields. |
| `super().validate()` | Ensures parent validation still runs. |

The main design idea is:

> Each builder validates the fields it owns, then delegates upward with `super().validate()`.

This avoids awkward method names like `_validate_common_fields()` and scales better if the hierarchy gets one or two levels deeper.

---

## 9. When to be careful

This approach is good for shallow inheritance.

If the hierarchy becomes very deep, builder inheritance may become awkward:

```text
MessageBuilder
└── EmailMessageBuilder
    └── MarketingEmailBuilder
        └── PromotionalEmailBuilder
```

At that point, composition or builder facets may be clearer.

A useful rule:

> Builder inheritance is good when the final objects have a real inheritance relationship and the builder hierarchy stays shallow.

---

[Back to exercise](exercise3.md) · [Solution script](exercise3_solution.py)
