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
        # TODO: validate everything
        # TODO: return Notification(...)
        pass