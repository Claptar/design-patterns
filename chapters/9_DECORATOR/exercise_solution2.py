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


class LoggingDecorator(NotifierDecorator):
    def send(self, recipient: str, message: str) -> None:
        print(f"SENDING notification to {recipient}")
        self._wrapped.send(recipient, message)
        print(f"SENT notification to {recipient}")


class RetryDecorator(NotifierDecorator):
    def __init__(self, wrapped: Notifier, max_retries: int = 3):
        super().__init__(wrapped)
        self._max_retries = max_retries

    def send(self, recipient: str, message: str) -> None:
        last_error = None

        for attempt in range(1, self._max_retries + 1):
            try:
                self._wrapped.send(recipient, message)
                return
            except Exception as e:
                last_error = e
                if attempt < self._max_retries:
                    print(f"Retry {attempt}/{self._max_retries}...")

        raise last_error


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
    # RateLimitDecorator is outermost — it blocks BEFORE LoggingDecorator runs.
    # So blocked sends are never logged.
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
    # LoggingDecorator is outermost — it logs BEFORE the rate limit check runs.
    # So even blocked sends appear in the log.
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
    # Reading order (outside in):
    # 1. LoggingDecorator — log every attempt, including blocked ones
    # 2. RateLimitDecorator — enforce rate limit
    # 3. RetryDecorator — retry transient failures
    # 4. PrefixDecorator — prepend [ALERT] to message
    # 5. EmailNotifier — actually send
    notifier = LoggingDecorator(
        RateLimitDecorator(
            RetryDecorator(
                PrefixDecorator(EmailNotifier(), prefix="[ALERT] "),
                max_retries=2,
            ),
            limit=10,
        )
    )
    notifier.send("ops@example.com", "disk usage at 95%")
    print()


if __name__ == "__main__":
    test_retry()
    test_rate_limit()
    test_ordering()
    test_production_composition()
