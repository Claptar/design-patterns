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
        self._recipient_builder = NotificationRecipientBuilder(self)
        self._content_builder = NotificationContentBuilder(self)
        self._delivery_builder = NotificationDeliveryBuilder(self)
        self._importance_builder = NotificationImportanceBuilder(self)
    
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
    
    def build(self) -> Notification:
        # Validation
        if not self._recipient:
            raise ValueError("Recipient is required")
        if not self._title:
            raise ValueError("Title is required")
        if self._channel not in ["email", "sms"]:
            raise ValueError("Channel must be 'email' or 'sms'")
        if self._priority not in ["low", "normal", "high"]:
            raise ValueError("Priority must be 'low', 'normal', or 'high'")
        
        if self._retry_count < 0:
            raise ValueError("Retry count cannot be negative")
        if self._send_after_minutes is not None and self._send_after_minutes < 0:
            raise ValueError("Send after minutes cannot be negative")
        

        return Notification(
            recipient=self._recipient,
            title=self._title,
            body=self._body,
            channel=self._channel,
            priority=self._priority,
            retry_count=self._retry_count,
            send_after_minutes=self._send_after_minutes
        )

class BaseBuilder:
    def __init__(self, root_builder):
        self._root_builder = root_builder
    
    @property
    def recipient(self):
        return self._root_builder.recipient
    
    @property
    def content(self):
        return self._root_builder.content
    
    @property
    def delivery(self):
        return self._root_builder.delivery
    
    @property
    def importance(self):
        return self._root_builder.importance
    
    def build(self):
        return self._root_builder.build()
        
    
class NotificationRecipientBuilder(BaseBuilder):
    def to(self, recipient: str):
        self._root_builder._recipient = recipient
        return self
    
class NotificationContentBuilder(BaseBuilder):
    def titled(self, title: str):
        self._root_builder._title = title
        return self
    
    def with_body(self, body: str):
        self._root_builder._body = body
        return self
    
class NotificationDeliveryBuilder(BaseBuilder):
    def via_email(self):
        self._root_builder._channel = "email"
        return self
    
    def via_sms(self):
        self._root_builder._channel = "sms"
        return self
    
    def send_after(self, minutes: int):
        self._root_builder._send_after_minutes = minutes
        return self
    
    def retrying(self, count: int):
        self._root_builder._retry_count = count
        return self
    
class NotificationImportanceBuilder(BaseBuilder):
    def normal_priority(self):
        self._root_builder._priority = "normal"
        return self
    
    def low_priority(self):
        self._root_builder._priority = "low"
        return self
    
    def high_priority(self):
        self._root_builder._priority = "high"
        return self


if __name__ == "__main__":
    # Test case 1: No recipient
    try:
        notification = (
            NotificationBuilder()
            .content
                .titled("Hello")
            .build()
        )
    except ValueError as e:
        print(f"Error: {e}")

    # Test case 2: Negative retry count
    try:
        notification = (
            NotificationBuilder()
            .recipient
                .to("alice@example.com")
            .content
                .titled("Hello")
            .delivery
                .retrying(-1)
            .build()
        )
    except ValueError as e:
        print(f"Error: {e}")
    
    # Test case 3: Valid notification
    try:
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
    except ValueError as e:
        print(f"Error: {e}")
        