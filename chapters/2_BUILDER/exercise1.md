---
layout: default
title: Exercise 1: Notification Builder
---

# Exercise 1: Build a notification builder

Now practice the basic Builder idea with a small existing class.

You are given this final object. Do **not** change it.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Notification:
    recipient: str
    title: str
    body: str
    channel: str
    priority: str
    retry_count: int
    send_after_minutes: int | None
```

Your task is to implement a `NotificationBuilder` that creates a valid `Notification`.

The final usage should look like this:

```python
notification = (
    NotificationBuilder()
    .to("alice@example.com")
    .titled("Payment received")
    .with_body("Your payment was successfully processed.")
    .via_email()
    .high_priority()
    .retrying(3)
    .send_after(10)
    .build()
)
```

The builder should support these methods:

```text
.to(recipient)
.titled(title)
.with_body(body)
.via_email()
.via_sms()
.low_priority()
.normal_priority()
.high_priority()
.retrying(count)
.send_after(minutes)
.build()
```

Use these defaults:

| Field | Default |
|---|---|
| `body` | `""` |
| `channel` | `"email"` |
| `priority` | `"normal"` |
| `retry_count` | `0` |
| `send_after_minutes` | `None` |

Validation rules:

- `recipient` is required.
- `title` is required.
- `channel` must be either `"email"` or `"sms"`.
- `priority` must be `"low"`, `"normal"`, or `"high"`.
- `retry_count` cannot be negative.
- `send_after_minutes` cannot be negative.

This should fail because there is no recipient:

```python
notification = (
    NotificationBuilder()
    .titled("Hello")
    .build()
)
```

This should fail because the retry count is negative:

```python
notification = (
    NotificationBuilder()
    .to("alice@example.com")
    .titled("Hello")
    .retrying(-1)
    .build()
)
```

Start with this skeleton:

```python
class NotificationBuilder:
    def __init__(self):
        self._recipient = None
        self._title = None
        self._body = ""
        self._channel = "email"
        self._priority = "normal"
        self._retry_count = 0
        self._send_after_minutes = None

    def to(self, recipient):
        # TODO
        return self

    def titled(self, title):
        # TODO
        return self

    def with_body(self, body):
        # TODO
        return self

    def via_email(self):
        # TODO
        return self

    def via_sms(self):
        # TODO
        return self

    def low_priority(self):
        # TODO
        return self

    def normal_priority(self):
        # TODO
        return self

    def high_priority(self):
        # TODO
        return self

    def retrying(self, count):
        # TODO
        return self

    def send_after(self, minutes):
        # TODO
        return self

    def build(self):
        # TODO: validate required fields
        # TODO: validate invalid values
        # TODO: return Notification(...)
        pass
```

---

[Back to Builder](builder.md) · [Script](exercise1.py) · [Solution](solution1.md)
