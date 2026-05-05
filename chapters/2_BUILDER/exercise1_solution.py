from __future__ import annotations

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


def assert_raises(expected_error, callback):
    try:
        callback()
    except expected_error:
        return

    raise AssertionError(f"Expected {expected_error.__name__}")


def main():
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

    print(notification)

    assert notification == Notification(
        recipient="alice@example.com",
        title="Payment received",
        body="Your payment was successfully processed.",
        channel="email",
        priority="high",
        retry_count=3,
        send_after_minutes=10,
    )

    default_notification = (
        NotificationBuilder()
        .to("bob@example.com")
        .titled("Welcome")
        .build()
    )

    assert default_notification == Notification(
        recipient="bob@example.com",
        title="Welcome",
        body="",
        channel="email",
        priority="normal",
        retry_count=0,
        send_after_minutes=None,
    )

    assert_raises(
        ValueError,
        lambda: NotificationBuilder().titled("Hello").build(),
    )

    assert_raises(
        ValueError,
        lambda: (
            NotificationBuilder()
            .to("alice@example.com")
            .titled("Hello")
            .retrying(-1)
            .build()
        ),
    )

    assert_raises(
        ValueError,
        lambda: (
            NotificationBuilder()
            .to("alice@example.com")
            .titled("Hello")
            .send_after(-10)
            .build()
        ),
    )

    print("All checks passed.")


if __name__ == "__main__":
    main()
