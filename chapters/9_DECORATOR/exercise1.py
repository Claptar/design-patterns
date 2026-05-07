from abc import ABC, abstractmethod


class Notifier(ABC):
    @abstractmethod
    def send(self, recipient: str, message: str) -> None:
        pass


class EmailNotifier(Notifier):
    def send(self, recipient: str, message: str) -> None:
        print(f"EMAIL to {recipient}: {message}")


# TODO: implement LoggingDecorator
#
# class LoggingDecorator(Notifier):
#     ...


# TODO: implement UppercaseDecorator
#
# class UppercaseDecorator(Notifier):
#     ...


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
