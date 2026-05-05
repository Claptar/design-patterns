---
layout: default
title: Exercise 2: Notification Builder Facets
---

# Exercise 2: Build a faceted notification builder

In the previous exercise, you built one regular builder with all construction methods on a single class.

That works, but even a small builder can start to feel crowded when different methods belong to different areas.

For this exercise, refactor the notification builder into **builder facets**.

The final object is the same as before. Do **not** change it.

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

Your task is to implement a `NotificationBuilder` that exposes smaller builders for separate parts of the notification.

The final usage should look like this:

```python
notification = (
    NotificationBuilder()
    .recipient
        .to("alice@example.com")
    .content
        .titled("Payment received")
        .with_body("Your payment was successfully processed.")
    .delivery
        .via_email()
        .retrying(3)
        .send_after(10)
    .importance
        .high_priority()
    .build()
)
```

The important difference is that the methods are now grouped by responsibility:

| Facet | Responsibility |
|---|---|
| `recipient` | Who receives the notification. |
| `content` | The title and body of the notification. |
| `delivery` | The channel, retries, and delayed sending. |
| `importance` | The priority of the notification. |

---

## Requirements

Implement these classes:

```text
NotificationBuilder
NotificationFacet
RecipientFacet
ContentFacet
DeliveryFacet
ImportanceFacet
```

`NotificationBuilder` should be the root builder. It should own the data being collected and expose the facets.

The root builder should expose these properties:

```text
.recipient
.content
.delivery
.importance
```

Each facet should also allow moving to the other facets.

For example, this should work:

```python
notification = (
    NotificationBuilder()
    .recipient.to("alice@example.com")
    .content.titled("Welcome")
    .delivery.via_sms()
    .importance.normal_priority()
    .build()
)
```

This means that after calling a method on one facet, the chain should still be able to move to another facet.

---

## Facet methods

The `recipient` facet should support:

```text
.to(recipient)
```

The `content` facet should support:

```text
.titled(title)
.with_body(body)
```

The `delivery` facet should support:

```text
.via_email()
.via_sms()
.retrying(count)
.send_after(minutes)
```

The `importance` facet should support:

```text
.low_priority()
.normal_priority()
.high_priority()
```

All fluent methods should return `self`.

The shared base facet should make it possible to move between facets and call `.build()` from any facet.

---

## Defaults

Use the same defaults as the first exercise:

| Field | Default |
|---|---|
| `body` | `""` |
| `channel` | `"email"` |
| `priority` | `"normal"` |
| `retry_count` | `0` |
| `send_after_minutes` | `None` |

---

## Validation rules

The final `build()` method should validate the completed notification.

Rules:

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
    .content.titled("Hello")
    .build()
)
```

This should fail because the retry count is negative:

```python
notification = (
    NotificationBuilder()
    .recipient.to("alice@example.com")
    .content.titled("Hello")
    .delivery.retrying(-1)
    .build()
)
```

---

## Starter skeleton

```python
class NotificationBuilder:
    def __init__(self):
        self._recipient_value = None
        self._title = None
        self._body = ""
        self._channel = "email"
        self._priority = "normal"
        self._retry_count = 0
        self._send_after_minutes = None

        self._recipient = RecipientFacet(self)
        self._content = ContentFacet(self)
        self._delivery = DeliveryFacet(self)
        self._importance = ImportanceFacet(self)

    @property
    def recipient(self):
        return self._recipient

    @property
    def content(self):
        return self._content

    @property
    def delivery(self):
        return self._delivery

    @property
    def importance(self):
        return self._importance

    def build(self):
        # TODO: validate required fields
        # TODO: validate invalid values
        # TODO: return Notification(...)
        pass


class NotificationFacet:
    def __init__(self, root):
        self._root = root

    @property
    def recipient(self):
        # TODO
        pass

    @property
    def content(self):
        # TODO
        pass

    @property
    def delivery(self):
        # TODO
        pass

    @property
    def importance(self):
        # TODO
        pass

    def build(self):
        # TODO
        pass


class RecipientFacet(NotificationFacet):
    def to(self, recipient):
        # TODO
        return self


class ContentFacet(NotificationFacet):
    def titled(self, title):
        # TODO
        return self

    def with_body(self, body):
        # TODO
        return self


class DeliveryFacet(NotificationFacet):
    def via_email(self):
        # TODO
        return self

    def via_sms(self):
        # TODO
        return self

    def retrying(self, count):
        # TODO
        return self

    def send_after(self, minutes):
        # TODO
        return self


class ImportanceFacet(NotificationFacet):
    def low_priority(self):
        # TODO
        return self

    def normal_priority(self):
        # TODO
        return self

    def high_priority(self):
        # TODO
        return self
```

---

[Script](exercise2.py) · [My solution](my_exercise2_solution.py) · [Solution](solution2.md)
