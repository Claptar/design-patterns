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
    VALID_PRIORITIES = {"low", "normal", "high"}

    def __init__(self):
        self._recipient: str | None = None
        self._subject: str | None = None
        self._priority = "normal"

    def to(self, recipient: str) -> Self:
        self._recipient = recipient.strip().lower()
        return self

    def subject(self, subject: str) -> Self:
        self._subject = subject.strip()
        return self

    def low_priority(self) -> Self:
        self._priority = "low"
        return self

    def normal_priority(self) -> Self:
        self._priority = "normal"
        return self

    def high_priority(self) -> Self:
        self._priority = "high"
        return self

    def validate(self) -> None:
        if not self._recipient:
            raise ValueError("Recipient is required")

        if not self._subject:
            raise ValueError("Subject is required")

        if self._priority not in self.VALID_PRIORITIES:
            raise ValueError("Priority must be 'low', 'normal', or 'high'")

    def build(self) -> Message:
        self.validate()
        return Message(
            recipient=self._recipient,
            subject=self._subject,
            priority=self._priority,
        )


class EmailMessageBuilder(MessageBuilder):
    def __init__(self):
        super().__init__()
        self._html_body: str | None = None
        self._cc: list[str] = []
        self._bcc: list[str] = []

    def html(self, html_body: str) -> Self:
        self._html_body = html_body.strip()
        return self

    def cc(self, recipient: str) -> Self:
        recipient = recipient.strip().lower()
        if not recipient:
            raise ValueError("CC recipient cannot be blank")

        self._cc.append(recipient)
        return self

    def bcc(self, recipient: str) -> Self:
        recipient = recipient.strip().lower()
        if not recipient:
            raise ValueError("BCC recipient cannot be blank")

        self._bcc.append(recipient)
        return self

    def validate(self) -> None:
        super().validate()

        if not self._html_body:
            raise ValueError("HTML body is required")

    def build(self) -> EmailMessage:
        self.validate()
        return EmailMessage(
            recipient=self._recipient,
            subject=self._subject,
            priority=self._priority,
            html_body=self._html_body,
            cc=tuple(self._cc),
            bcc=tuple(self._bcc),
        )


if __name__ == "__main__":
    email = (
        EmailMessageBuilder()
        .to("ALICE@EXAMPLE.COM")
        .subject(" Your invoice ")
        .high_priority()
        .html(" <p>Thanks for your purchase.</p> ")
        .cc("ACCOUNTS@EXAMPLE.COM")
        .bcc("AUDIT@EXAMPLE.COM")
        .build()
    )

    print(email)

    try:
        EmailMessageBuilder().to("alice@example.com").subject("Hello").build()
    except ValueError as error:
        print(f"Error: {error}")
