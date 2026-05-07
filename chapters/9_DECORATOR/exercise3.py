from abc import ABC, abstractmethod


class Notifier(ABC):
    @abstractmethod
    def send(self, recipient: str, message: str) -> None:
        pass


class RateLimitExceeded(Exception):
    pass


class EmailNotifier(Notifier):
    def __init__(self):
        self._sent_count = 0
        self._from = "no-reply@example.com"
        self._reply_to = None

    def send(self, recipient: str, message: str) -> None:
        self._sent_count += 1
        print(f"EMAIL to {recipient}: {message}")

    def set_from_address(self, address: str) -> None:
        self._from = address
        print(f"From address set to {address}")

    def set_reply_to(self, address: str) -> None:
        self._reply_to = address
        print(f"Reply-to set to {address}")

    def get_sent_count(self) -> int:
        return self._sent_count

    def flush_queue(self) -> None:
        print("Queue flushed")


# Part A and B: the base decorator WITHOUT __getattr__
class NotifierDecorator(Notifier):
    def __init__(self, wrapped: Notifier):
        self._wrapped = wrapped

    def send(self, recipient: str, message: str) -> None:
        self._wrapped.send(recipient, message)

    # TODO Part B: add manual forwarding methods here
    # def set_from_address(self, address: str) -> None: ...
    # def set_reply_to(self, address: str) -> None: ...
    # def get_sent_count(self) -> int: ...
    # def flush_queue(self) -> None: ...


class LoggingDecorator(NotifierDecorator):
    def send(self, recipient: str, message: str) -> None:
        print(f"SENDING notification to {recipient}")
        self._wrapped.send(recipient, message)
        print(f"SENT notification to {recipient}")


class RateLimitDecorator(NotifierDecorator):
    def __init__(self, wrapped: Notifier, limit: int = 5):
        super().__init__(wrapped)
        self._limit = limit
        self._count = 0

    def send(self, recipient: str, message: str) -> None:
        if self._count >= self._limit:
            raise RateLimitExceeded(
                f"Rate limit of {self._limit} notifications exceeded"
            )
        self._count += 1
        self._wrapped.send(recipient, message)


class PrefixDecorator(NotifierDecorator):
    def __init__(self, wrapped: Notifier, prefix: str = "[URGENT] "):
        super().__init__(wrapped)
        self._prefix = prefix

    def send(self, recipient: str, message: str) -> None:
        self._wrapped.send(recipient, f"{self._prefix}{message}")


# ─── tests ────────────────────────────────────────────────────────────────────

def test_type_erosion():
    """Part A: observe the AttributeError."""
    print("─── test_type_erosion ───")
    notifier = LoggingDecorator(EmailNotifier())
    try:
        notifier.set_from_address("alerts@company.com")
    except AttributeError as e:
        print(f"AttributeError: {e}")
    print()


def test_manual_forwarding():
    """Part B: test after adding manual forwarding methods."""
    print("─── test_manual_forwarding ───")
    notifier = LoggingDecorator(EmailNotifier())
    notifier.set_from_address("alerts@company.com")
    notifier.set_reply_to("noreply@company.com")
    notifier.send("alice@example.com", "hello")
    print(f"Sent count: {notifier.get_sent_count()}")
    notifier.flush_queue()
    print()


def test_transparent_decorator():
    """Part C: test after adding __getattr__ to NotifierDecorator."""
    print("─── test_transparent_decorator ───")
    notifier = LoggingDecorator(EmailNotifier())
    notifier.set_from_address("alerts@company.com")
    notifier.set_reply_to("noreply@company.com")
    notifier.send("alice@example.com", "hello")
    print(f"Sent count: {notifier.get_sent_count()}")
    notifier.flush_queue()
    print()


def test_stacked_transparent():
    """Part D: test __getattr__ forwarding through a full stack."""
    print("─── test_stacked_transparent ───")
    notifier = LoggingDecorator(
        RateLimitDecorator(
            PrefixDecorator(EmailNotifier(), prefix="[ALERT] "),
            limit=10,
        )
    )
    notifier.set_from_address("alerts@company.com")
    notifier.send("alice@example.com", "disk at 95%")
    print(f"Sent count: {notifier.get_sent_count()}")
    print()


def test_type_hint_limitation():
    """Part E: runtime works, type checker complains."""
    print("─── test_type_hint_limitation ───")

    def configure_notifier(notifier: EmailNotifier) -> None:
        notifier.set_from_address("alerts@company.com")
        notifier.set_reply_to("noreply@company.com")

    # This works at runtime — does a type checker agree?
    configure_notifier(LoggingDecorator(EmailNotifier()))  # type: ignore
    print()


if __name__ == "__main__":
    test_type_erosion()
    # Uncomment as you complete each part:
    # test_manual_forwarding()
    # test_transparent_decorator()
    # test_stacked_transparent()
    # test_type_hint_limitation()
