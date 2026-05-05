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
        # TODO: validate required fields
        # TODO: validate invalid values
        # TODO: return Notification(...)
        pass


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
