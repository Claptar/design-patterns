from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self


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


class MessageBuilder:
    def __init__(self):
        self._recipient = None
        self._subject = None
        self._priority = "normal"

    def to(self, recipient: str) -> Self:
        # TODO: normalize recipient by stripping whitespace and lowercasing
        return self

    def subject(self, subject: str) -> Self:
        # TODO: strip whitespace
        return self

    def low_priority(self) -> Self:
        # TODO
        return self

    def normal_priority(self) -> Self:
        # TODO
        return self

    def high_priority(self) -> Self:
        # TODO
        return self

    def build(self) -> Message:
        # TODO: validate recipient
        # TODO: validate subject
        # TODO: validate priority
        # TODO: return Message(...)
        pass


class EmailMessageBuilder(MessageBuilder):
    def __init__(self):
        super().__init__()
        self._html_body = None
        self._cc = []
        self._bcc = []

    def html(self, html_body: str) -> Self:
        # TODO: strip whitespace
        return self

    def cc(self, recipient: str) -> Self:
        # TODO: normalize recipient by stripping whitespace and lowercasing
        return self

    def bcc(self, recipient: str) -> Self:
        # TODO: normalize recipient by stripping whitespace and lowercasing
        return self

    def build(self) -> EmailMessage:
        # TODO: validate common Message fields
        # TODO: validate EmailMessage-specific fields
        # TODO: return EmailMessage(...)
        pass


if __name__ == "__main__":
    # Try your implementation here.
    email = (
        EmailMessageBuilder()
        .to("ALICE@EXAMPLE.COM")
        .subject(" Your invoice ")
        .normal_priority()
        .html(" <p>Thanks for your purchase.</p> ")
        .cc("ACCOUNTS@EXAMPLE.COM")
        .bcc("AUDIT@EXAMPLE.COM")
        .build()
    )
    print(email)
