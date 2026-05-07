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


# Part C solution: __getattr__ in the base replaces all manual forwarding
class NotifierDecorator(Notifier):
    def __init__(self, wrapped: Notifier):
        self._wrapped = wrapped

    def send(self, recipient: str, message: str) -> None:
        self._wrapped.send(recipient, message)

    def __getattr__(self, name: str):
        # Only fires when normal lookup fails (i.e. the decorator
        # does not have the attribute itself).
        return getattr(self._wrapped, name)


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
    """Part A: observe the AttributeError — run BEFORE the __getattr__ fix."""
    print("─── test_type_erosion ───")
    # With __getattr__ in place this no longer raises — comment out
    # NotifierDecorator.__getattr__ to observe the original problem.
    notifier = LoggingDecorator(EmailNotifier())
    try:
        notifier.set_from_address("alerts@company.com")
        print("set_from_address succeeded (transparent decorator is in place)")
    except AttributeError as e:
        print(f"AttributeError: {e}")
    print()


def test_transparent_decorator():
    """Part C: single decorator, all methods accessible."""
    print("─── test_transparent_decorator ───")
    notifier = LoggingDecorator(EmailNotifier())
    notifier.set_from_address("alerts@company.com")
    notifier.set_reply_to("noreply@company.com")
    notifier.send("alice@example.com", "hello")
    print(f"Sent count: {notifier.get_sent_count()}")
    notifier.flush_queue()
    print()


def test_stacked_transparent():
    """Part D: __getattr__ chains through the full stack."""
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
    """Part E: runtime works, static type checker disagrees."""
    print("─── test_type_hint_limitation ───")

    def configure_notifier(notifier: EmailNotifier) -> None:
        notifier.set_from_address("alerts@company.com")
        notifier.set_reply_to("noreply@company.com")

    # Works at runtime: __getattr__ forwards set_from_address and set_reply_to
    # to the inner EmailNotifier.
    #
    # A type checker (mypy, pyright) will flag this line because
    # LoggingDecorator is not a subtype of EmailNotifier — it only
    # promises the Notifier interface (just send()).
    #
    # The trade-off: runtime transparency vs static type safety.
    # If you need both, you must either:
    #   - add __getattr__ type stubs, or
    #   - make decorators generic (NotifierDecorator[T]) and propagate T, or
    #   - accept the type: ignore comment at the call site.
    configure_notifier(LoggingDecorator(EmailNotifier()))  # type: ignore
    print()


if __name__ == "__main__":
    test_type_erosion()
    test_transparent_decorator()
    test_stacked_transparent()
    test_type_hint_limitation()
