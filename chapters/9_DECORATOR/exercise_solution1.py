from abc import ABC, abstractmethod


class Notifier(ABC):
    @abstractmethod
    def send(self, recipient: str, message: str) -> None:
        pass


class EmailNotifier(Notifier):
    def send(self, recipient: str, message: str) -> None:
        print(f"EMAIL to {recipient}: {message}")


class LoggingDecorator(Notifier):
    def __init__(self, wrapped: Notifier):
        self._wrapped = wrapped

    def send(self, recipient: str, message: str) -> None:
        print(f"SENDING notification to {recipient}")
        self._wrapped.send(recipient, message)
        print(f"SENT notification to {recipient}")


class UppercaseDecorator(Notifier):
    def __init__(self, wrapped: Notifier):
        self._wrapped = wrapped

    def send(self, recipient: str, message: str) -> None:
        self._wrapped.send(recipient, message.upper())


# ─── tests ────────────────────────────────────────────────────────────────────

def test_logging_decorator():
    print("─── test_logging_decorator ───")
    notifier = LoggingDecorator(EmailNotifier())
    notifier.send("alice@example.com", "Meeting at 3pm")
    print()


def test_uppercase_decorator():
    print("─── test_uppercase_decorator ───")
    notifier = UppercaseDecorator(EmailNotifier())
    notifier.send("bob@example.com", "server is down")
    print()


def test_composed():
    print("─── test_composed ───")
    notifier = LoggingDecorator(UppercaseDecorator(EmailNotifier()))
    notifier.send("bob@example.com", "server is down")
    print()


if __name__ == "__main__":
    test_logging_decorator()
    test_uppercase_decorator()
    test_composed()
