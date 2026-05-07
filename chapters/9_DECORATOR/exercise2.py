from abc import ABC, abstractmethod


class Notifier(ABC):
    @abstractmethod
    def send(self, recipient: str, message: str) -> None:
        pass


class RateLimitExceeded(Exception):
    pass


class EmailNotifier(Notifier):
    def send(self, recipient: str, message: str) -> None:
        print(f"EMAIL to {recipient}: {message}")


class SmsNotifier(Notifier):
    def send(self, recipient: str, message: str) -> None:
        print(f"SMS to {recipient}: {message[:160]}")


class PushNotifier(Notifier):
    def send(self, recipient: str, message: str) -> None:
        print(f"PUSH to {recipient}: {message[:100]}")


class NotifierDecorator(Notifier):
    def __init__(self, wrapped: Notifier):
        self._wrapped = wrapped

    def send(self, recipient: str, message: str) -> None:
        self._wrapped.send(recipient, message)


# TODO: implement LoggingDecorator
# Prints "SENDING notification to {recipient}" before
# and "SENT notification to {recipient}" after.
#
# class LoggingDecorator(NotifierDecorator):
#     ...


# TODO: implement RetryDecorator
# Retries up to max_retries times if the inner send raises.
# Prints "Retry {n}/{max_retries}..." on each retry.
# Re-raises the last exception if all retries fail.
#
# class RetryDecorator(NotifierDecorator):
#     def __init__(self, wrapped: Notifier, max_retries: int = 3):
#         ...


# TODO: implement RateLimitDecorator
# Raises RateLimitExceeded once the per-instance limit is reached.
#
# class RateLimitDecorator(NotifierDecorator):
#     def __init__(self, wrapped: Notifier, limit: int = 5):
#         ...


# TODO: implement PrefixDecorator
# Prepends a fixed string to every message.
#
# class PrefixDecorator(NotifierDecorator):
#     def __init__(self, wrapped: Notifier, prefix: str = "[URGENT] "):
#         ...


# ─── tests ────────────────────────────────────────────────────────────────────

def test_retry():
    print("─── test_retry ───")

    class FlakyNotifier(Notifier):
        def __init__(self):
            self._attempts = 0

        def send(self, recipient: str, message: str) -> None:
            self._attempts += 1
            if self._attempts < 3:
                raise ConnectionError("Network error")
            print(f"EMAIL to {recipient}: {message}")

    notifier = RetryDecorator(FlakyNotifier(), max_retries=3)
    notifier.send("alice@example.com", "hello")
    print()


def test_rate_limit():
    print("─── test_rate_limit ───")
    notifier = RateLimitDecorator(EmailNotifier(), limit=3)
    for i in range(4):
        try:
            notifier.send("alice@example.com", f"message {i+1}")
        except RateLimitExceeded as e:
            print(f"Blocked: {e}")
    print()


def test_ordering():
    print("─── test_ordering: rate_limit outside logging ───")
    notifier_a = RateLimitDecorator(
        LoggingDecorator(EmailNotifier()),
        limit=2,
    )
    for i in range(3):
        try:
            notifier_a.send("alice@example.com", f"message {i+1}")
        except RateLimitExceeded as e:
            print(f"Blocked: {e}")
    print()

    print("─── test_ordering: logging outside rate_limit ───")
    notifier_b = LoggingDecorator(
        RateLimitDecorator(EmailNotifier(), limit=2)
    )
    for i in range(3):
        try:
            notifier_b.send("alice@example.com", f"message {i+1}")
        except RateLimitExceeded as e:
            print(f"Blocked: {e}")
    print()


def test_production_composition():
    print("─── test_production_composition ───")
    # TODO: build the production alert notifier described in Part C
    # notifier = ...
    # notifier.send("ops@example.com", "disk usage at 95%")
    print()


if __name__ == "__main__":
    test_retry()
    test_rate_limit()
    test_ordering()
    test_production_composition()
