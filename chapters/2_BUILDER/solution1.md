---
layout: default
title: Notification Builder Solution
---

# Notification Builder Solution

This is one possible solution to the notification builder exercise.

The final `Notification` class stays simple and immutable. The builder is responsible for collecting construction values, applying defaults, validating the result, and creating the final object.

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

The important idea is that `Notification` represents a completed notification. It should not need to know about the step-by-step process used to create one.

That construction process belongs in `NotificationBuilder`.

---

## Implementation choices

Before looking at the full implementation, it is worth noticing a few design choices.

### 1. The final object is immutable

```python
@dataclass(frozen=True)
class Notification:
    ...
```

The notification is marked as frozen because, after construction, we want it to behave like a finished value.

The builder can be mutable while we are still deciding what the notification should look like. Once `build()` returns a `Notification`, the result should be complete and stable.

This gives us a clean split:

```text
NotificationBuilder -> mutable object under construction
Notification        -> immutable completed result
```

### 2. Defaults live in the builder

The optional values are initialized in `__init__`:

```python
self._body = ""
self._channel = "email"
self._priority = "normal"
self._retry_count = 0
self._send_after_minutes = None
```

This means the caller only has to provide the values that are truly required.

For example, this is enough:

```python
notification = (
    NotificationBuilder()
    .to("bob@example.com")
    .titled("Welcome")
    .build()
)
```

The caller does not need to remember that the default channel is email, the default priority is normal, or that retry count starts at zero. Those choices are centralized in the builder.

### 3. Required values start as `None`

The required values start empty:

```python
self._recipient = None
self._title = None
```

This lets `build()` distinguish between values that were provided and values that were forgotten.

The builder can then reject incomplete construction:

```python
if not self._recipient:
    raise ValueError("Recipient is required")

if not self._title:
    raise ValueError("Title is required")
```

This is nicer than allowing a half-valid `Notification` object to exist.

### 4. Fluent methods return `self`

Every configuration method ends with:

```python
return self
```

That is what allows this style:

```python
notification = (
    NotificationBuilder()
    .to("alice@example.com")
    .titled("Payment received")
    .high_priority()
    .build()
)
```

Each method updates the builder and then returns the same builder object so the next method can continue the chain.

### 5. Validation is centralized in `build()`

The method `build()` is the final checkpoint.

That is where we check whether the builder has enough information to produce a valid `Notification`.

This is useful because the caller may set values in different orders:

```python
NotificationBuilder().to("alice@example.com").titled("Hello").build()
NotificationBuilder().titled("Hello").to("alice@example.com").build()
```

Both should be allowed. The important question is not the order of the calls. The important question is whether the final state is valid when `build()` is called.

---

## Builder implementation

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
        self._recipient = recipient.strip()
        return self

    def titled(self, title):
        self._title = title.strip()
        return self

    def with_body(self, body):
        self._body = body
        return self

    def via_email(self):
        self._channel = "email"
        return self

    def via_sms(self):
        self._channel = "sms"
        return self

    def low_priority(self):
        self._priority = "low"
        return self

    def normal_priority(self):
        self._priority = "normal"
        return self

    def high_priority(self):
        self._priority = "high"
        return self

    def retrying(self, count):
        self._retry_count = count
        return self

    def send_after(self, minutes):
        self._send_after_minutes = minutes
        return self

    def build(self):
        if not self._recipient:
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
            recipient=self._recipient,
            title=self._title,
            body=self._body,
            channel=self._channel,
            priority=self._priority,
            retry_count=self._retry_count,
            send_after_minutes=self._send_after_minutes,
        )
```

---

## Walking through the builder

### `__init__` stores construction state

The builder stores temporary values in private attributes:

```python
self._recipient = None
self._title = None
self._body = ""
```

These attributes are not the final object yet. They are just the builder's working state.

This is one of the main differences between a builder and a constructor call. A constructor creates the object immediately. A builder lets construction happen gradually.

### `to()` and `titled()` normalize simple text

```python
def to(self, recipient):
    self._recipient = recipient.strip()
    return self


def titled(self, title):
    self._title = title.strip()
    return self
```

Both methods call `.strip()` because leading and trailing spaces are probably accidental.

For example:

```python
.to(" alice@example.com ")
```

should behave like:

```python
.to("alice@example.com")
```

The builder is a good place for this kind of small normalization because it keeps callers from repeating it everywhere.

### `via_email()` and `via_sms()` avoid stringly typed calls

Instead of asking the caller to write this:

```python
.with_channel("email")
```

we provide intention-revealing methods:

```python
.via_email()
.via_sms()
```

This makes the calling code easier to read and harder to mistype.

A typo like this is easy to miss:

```python
.with_channel("emial")
```

But this is much clearer:

```python
.via_email()
```

The same idea is used for priority:

```python
.low_priority()
.normal_priority()
.high_priority()
```

### `retrying()` and `send_after()` defer validation

These methods simply store the values:

```python
def retrying(self, count):
    self._retry_count = count
    return self


def send_after(self, minutes):
    self._send_after_minutes = minutes
    return self
```

The validation happens later in `build()`.

For a small builder like this, either approach is reasonable:

- validate immediately inside each method
- store values first and validate everything inside `build()`

This solution chooses `build()` as the single validation point. That keeps the fluent methods simple and makes it easy to see all final construction rules in one place.

### `build()` protects the final object

The most important method is `build()`.

It refuses to create a `Notification` if the builder is incomplete or invalid:

```python
if not self._recipient:
    raise ValueError("Recipient is required")

if self._retry_count < 0:
    raise ValueError("Retry count cannot be negative")
```

Only after validation passes does it create the final object:

```python
return Notification(
    recipient=self._recipient,
    title=self._title,
    body=self._body,
    channel=self._channel,
    priority=self._priority,
    retry_count=self._retry_count,
    send_after_minutes=self._send_after_minutes,
)
```

That means the rest of the program can trust that a `Notification` returned by the builder is valid according to the builder's rules.

---

## Example usage

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

The produced object is:

```python
Notification(
    recipient="alice@example.com",
    title="Payment received",
    body="Your payment was successfully processed.",
    channel="email",
    priority="high",
    retry_count=3,
    send_after_minutes=10,
)
```

This reads almost like a sentence:

```text
Build a notification to Alice, titled Payment received, sent by email, high priority, retrying 3 times, sent after 10 minutes.
```

That readability is one of the practical benefits of a builder.

---

## Example with defaults

The builder also works when optional values are not provided.

```python
notification = (
    NotificationBuilder()
    .to("bob@example.com")
    .titled("Welcome")
    .build()
)
```

This produces:

```python
Notification(
    recipient="bob@example.com",
    title="Welcome",
    body="",
    channel="email",
    priority="normal",
    retry_count=0,
    send_after_minutes=None,
)
```

The caller provided only the required information. The builder filled in the rest.

---

## Invalid examples

This fails because `recipient` is required:

```python
notification = (
    NotificationBuilder()
    .titled("Hello")
    .build()
)
```

This fails because `retry_count` cannot be negative:

```python
notification = (
    NotificationBuilder()
    .to("alice@example.com")
    .titled("Hello")
    .retrying(-1)
    .build()
)
```

This fails because `send_after_minutes` cannot be negative:

```python
notification = (
    NotificationBuilder()
    .to("alice@example.com")
    .titled("Hello")
    .send_after(-10)
    .build()
)
```

These examples are useful because they show that the builder is not only a prettier constructor. It also controls whether construction is allowed to finish.

---

## Why this is a builder

The builder gives object construction a dedicated place.

It handles:

- default values
- step-by-step construction
- validation before the final object exists
- readable method chaining
- creation of an immutable final object

The important separation is:

```text
Notification        -> stores the completed notification
NotificationBuilder -> knows how to construct a valid notification
```

In this small example, the builder may still look a little more verbose than using the constructor directly. That is normal. The point of the exercise is to practice the shape of the pattern on a small object before using it on objects where construction has more rules.
