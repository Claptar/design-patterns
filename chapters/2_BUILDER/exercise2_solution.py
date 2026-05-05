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


if __name__ == "__main__":
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

    print(notification)
