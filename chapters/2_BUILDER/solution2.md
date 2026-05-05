---
layout: default
title: Solution 2: Notification Builder Facets
---

# Solution 2: Notification Builder Facets

This is the solution for **Exercise 2: Build a faceted notification builder**.

The exercise asks for a `NotificationBuilder` that exposes smaller builders, or **facets**, for separate parts of a notification:

| Facet | Responsibility |
|---|---|
| `recipient` | Who receives the notification. |
| `content` | The title and body of the notification. |
| `delivery` | The channel, retries, and delayed sending. |
| `importance` | The priority of the notification. |

The final usage should support this style:

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

Full Python implementation: [`exercise2_solution.py`](sandbox:/mnt/data/exercise2_solution.py)

---

## 1. Final object

The final object stays exactly as required by the exercise:

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

The builder collects the values. The `Notification` object is created only when `.build()` is called.

---

## 2. Root builder

`NotificationBuilder` is the root builder. It owns the values being collected and exposes the four facets.

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

        self._recipient_builder = RecipientFacet(self)
        self._content_builder = ContentFacet(self)
        self._delivery_builder = DeliveryFacet(self)
        self._importance_builder = ImportanceFacet(self)
```

The internal names use `_recipient_builder`, `_content_builder`, and so on because those fields store **facet builder objects**, not the actual notification values.

The public properties stay clean:

```python
    @property
    def recipient(self):
        return self._recipient_builder

    @property
    def content(self):
        return self._content_builder

    @property
    def delivery(self):
        return self._delivery_builder

    @property
    def importance(self):
        return self._importance_builder
```

That keeps the fluent API readable:

```python
NotificationBuilder().recipient.to("alice@example.com")
```

---

## 3. Shared facet base

All facets inherit from `NotificationFacet`.

Its job is to let each facet move to the other facets and call `.build()`.

```python
class NotificationFacet:
    def __init__(self, root):
        self._root = root

    @property
    def recipient(self):
        return self._root.recipient

    @property
    def content(self):
        return self._root.content

    @property
    def delivery(self):
        return self._root.delivery

    @property
    def importance(self):
        return self._root.importance

    def build(self):
        return self._root.build()
```

This is what allows chains like this:

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

After `.recipient.to(...)`, the chain is still on a facet object. Because every facet inherits from `NotificationFacet`, it can move to `.content`, `.delivery`, `.importance`, or `.build()`.

---

## 4. Recipient facet

The recipient facet owns the recipient-related construction method.

```python
class RecipientFacet(NotificationFacet):
    def to(self, recipient):
        self._root._recipient_value = recipient
        return self
```

The method returns `self`, so you can continue chaining from the same facet:

```python
NotificationBuilder().recipient.to("alice@example.com")
```

---

## 5. Content facet

The content facet owns the title and body.

```python
class ContentFacet(NotificationFacet):
    def titled(self, title):
        self._root._title = title
        return self

    def with_body(self, body):
        self._root._body = body
        return self
```

The default body is an empty string, so `.with_body(...)` is optional.

---

## 6. Delivery facet

The delivery facet owns channel, retry count, and delayed sending.

```python
class DeliveryFacet(NotificationFacet):
    def via_email(self):
        self._root._channel = "email"
        return self

    def via_sms(self):
        self._root._channel = "sms"
        return self

    def retrying(self, count):
        self._root._retry_count = count
        return self

    def send_after(self, minutes):
        self._root._send_after_minutes = minutes
        return self
```

The defaults are:

| Field | Default |
|---|---|
| `channel` | `"email"` |
| `retry_count` | `0` |
| `send_after_minutes` | `None` |

---

## 7. Importance facet

The importance facet owns priority.

```python
class ImportanceFacet(NotificationFacet):
    def low_priority(self):
        self._root._priority = "low"
        return self

    def normal_priority(self):
        self._root._priority = "normal"
        return self

    def high_priority(self):
        self._root._priority = "high"
        return self
```

The default priority is `"normal"`, so this facet is optional unless the caller wants low or high priority.

---

## 8. Validation in `build()`

The root builder validates the completed notification.

```python
    def build(self):
        if not self._recipient_value:
            raise ValueError("Recipient is required")

        if not self._title:
            raise ValueError("Title is required")

        if self._channel not in {"email", "sms"}:
            raise ValueError("Channel must be either 'email' or 'sms'")

        if self._priority not in {"low", "normal", "high"}:
            raise ValueError("Priority must be 'low', 'normal', or 'high'")

        if self._retry_count < 0:
            raise ValueError("Retry count cannot be negative")

        if self._send_after_minutes is not None and self._send_after_minutes < 0:
            raise ValueError("Send-after minutes cannot be negative")

        return Notification(
            recipient=self._recipient_value,
            title=self._title,
            body=self._body,
            channel=self._channel,
            priority=self._priority,
            retry_count=self._retry_count,
            send_after_minutes=self._send_after_minutes,
        )
```

Validation belongs in `build()` because only the root builder has the complete picture.

For example, this fails because there is no recipient:

```python
notification = (
    NotificationBuilder()
    .content.titled("Hello")
    .build()
)
```

This fails because the retry count is negative:

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

## 9. Complete solution

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


class NotificationBuilder:
    def __init__(self):
        self._recipient_value = None
        self._title = None
        self._body = ""
        self._channel = "email"
        self._priority = "normal"
        self._retry_count = 0
        self._send_after_minutes = None

        self._recipient_builder = RecipientFacet(self)
        self._content_builder = ContentFacet(self)
        self._delivery_builder = DeliveryFacet(self)
        self._importance_builder = ImportanceFacet(self)

    @property
    def recipient(self):
        return self._recipient_builder

    @property
    def content(self):
        return self._content_builder

    @property
    def delivery(self):
        return self._delivery_builder

    @property
    def importance(self):
        return self._importance_builder

    def build(self):
        if not self._recipient_value:
            raise ValueError("Recipient is required")

        if not self._title:
            raise ValueError("Title is required")

        if self._channel not in {"email", "sms"}:
            raise ValueError("Channel must be either 'email' or 'sms'")

        if self._priority not in {"low", "normal", "high"}:
            raise ValueError("Priority must be 'low', 'normal', or 'high'")

        if self._retry_count < 0:
            raise ValueError("Retry count cannot be negative")

        if self._send_after_minutes is not None and self._send_after_minutes < 0:
            raise ValueError("Send-after minutes cannot be negative")

        return Notification(
            recipient=self._recipient_value,
            title=self._title,
            body=self._body,
            channel=self._channel,
            priority=self._priority,
            retry_count=self._retry_count,
            send_after_minutes=self._send_after_minutes,
        )


class NotificationFacet:
    def __init__(self, root):
        self._root = root

    @property
    def recipient(self):
        return self._root.recipient

    @property
    def content(self):
        return self._root.content

    @property
    def delivery(self):
        return self._root.delivery

    @property
    def importance(self):
        return self._root.importance

    def build(self):
        return self._root.build()


class RecipientFacet(NotificationFacet):
    def to(self, recipient):
        self._root._recipient_value = recipient
        return self


class ContentFacet(NotificationFacet):
    def titled(self, title):
        self._root._title = title
        return self

    def with_body(self, body):
        self._root._body = body
        return self


class DeliveryFacet(NotificationFacet):
    def via_email(self):
        self._root._channel = "email"
        return self

    def via_sms(self):
        self._root._channel = "sms"
        return self

    def retrying(self, count):
        self._root._retry_count = count
        return self

    def send_after(self, minutes):
        self._root._send_after_minutes = minutes
        return self


class ImportanceFacet(NotificationFacet):
    def low_priority(self):
        self._root._priority = "low"
        return self

    def normal_priority(self):
        self._root._priority = "normal"
        return self

    def high_priority(self):
        self._root._priority = "high"
        return self
```

---

## 10. Quick checks

Valid usage:

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

Shorter valid usage using defaults:

```python
notification = (
    NotificationBuilder()
    .recipient.to("alice@example.com")
    .content.titled("Welcome")
    .build()
)
```

This works because these defaults are already set:

| Field | Default |
|---|---|
| `body` | `""` |
| `channel` | `"email"` |
| `priority` | `"normal"` |
| `retry_count` | `0` |
| `send_after_minutes` | `None` |

---

## 11. Summary

This solution uses the faceted builder pattern:

- `NotificationBuilder` is the root builder.
- `NotificationFacet` is the shared base for all facets.
- `RecipientFacet`, `ContentFacet`, `DeliveryFacet`, and `ImportanceFacet` each own one area of construction.
- Facet methods return `self`.
- The shared base facet lets any facet move to another facet.
- `.build()` delegates back to the root builder.
- The final `Notification` object is created only after validation passes.

---

[Back to exercise](exercise2.md) · [Solution script](exercise2_solution.py) · [My solution](my_exercise2_solution.py)
