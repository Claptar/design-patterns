"""
Exercise 1 — Solution: Method Chain Logging Pipeline
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto


class LogLevel(Enum):
    DEBUG   = 1
    INFO    = 2
    WARNING = 3
    ERROR   = 4


@dataclass
class LogMessage:
    level: LogLevel
    text: str


class LogHandler(ABC):
    def __init__(self, name: str):
        self.name = name
        self._next: LogHandler | None = None

    def set_next(self, handler: LogHandler) -> LogHandler:
        self._next = handler
        return handler

    @abstractmethod
    def handle(self, message: LogMessage) -> None:
        ...

    def _pass_along(self, message: LogMessage) -> None:
        if self._next is not None:
            self._next.handle(message)


class DebugHandler(LogHandler):
    def __init__(self):
        super().__init__("DebugHandler")

    def handle(self, message: LogMessage) -> None:
        if message.level == LogLevel.DEBUG:
            print(f"[DEBUG] {message.text}")
        else:
            self._pass_along(message)


class InfoHandler(LogHandler):
    def __init__(self):
        super().__init__("InfoHandler")

    def handle(self, message: LogMessage) -> None:
        if message.level == LogLevel.INFO:
            print(f"[INFO]  {message.text}")
        else:
            self._pass_along(message)


class WarningHandler(LogHandler):
    def __init__(self):
        super().__init__("WarningHandler")

    def handle(self, message: LogMessage) -> None:
        if message.level == LogLevel.WARNING:
            print(f"[WARN]  {message.text}")
        else:
            self._pass_along(message)


class ErrorHandler(LogHandler):
    def __init__(self):
        super().__init__("ErrorHandler")

    def handle(self, message: LogMessage) -> None:
        if message.level == LogLevel.ERROR:
            print(f"[ERROR] {message.text}")
        else:
            self._pass_along(message)


def build_chain() -> LogHandler:
    debug   = DebugHandler()
    info    = InfoHandler()
    warning = WarningHandler()
    error   = ErrorHandler()
    debug.set_next(info).set_next(warning).set_next(error)
    return debug


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_each_level_reaches_correct_handler(capsys):
    chain = build_chain()
    chain.handle(LogMessage(LogLevel.DEBUG,   "hello from debug"))
    chain.handle(LogMessage(LogLevel.INFO,    "user logged in"))
    chain.handle(LogMessage(LogLevel.WARNING, "disk usage at 80%"))
    chain.handle(LogMessage(LogLevel.ERROR,   "database connection failed"))

    out = capsys.readouterr().out
    assert "[DEBUG] hello from debug"            in out
    assert "[INFO]  user logged in"              in out
    assert "[WARN]  disk usage at 80%"           in out
    assert "[ERROR] database connection failed"  in out


def test_message_handled_by_exactly_one_handler(capsys):
    chain = build_chain()
    chain.handle(LogMessage(LogLevel.INFO, "single message"))

    out = capsys.readouterr().out
    lines = [l for l in out.strip().splitlines() if l.strip()]
    assert len(lines) == 1
    assert "[INFO]" in lines[0]


def test_unknown_level_dropped_silently(capsys):
    debug = DebugHandler()
    info  = InfoHandler()
    debug.set_next(info)

    debug.handle(LogMessage(LogLevel.ERROR, "nobody home"))
    out = capsys.readouterr().out
    assert out.strip() == ""


if __name__ == "__main__":
    print("=== Part A ===")
    chain = build_chain()
    chain.handle(LogMessage(LogLevel.DEBUG,   "hello from debug"))
    chain.handle(LogMessage(LogLevel.INFO,    "user logged in"))
    chain.handle(LogMessage(LogLevel.WARNING, "disk usage at 80%"))
    chain.handle(LogMessage(LogLevel.ERROR,   "database connection failed"))

    print("\n=== Part B — with tracing ===")

    class TracingHandler(LogHandler):
        """Wraps any handler and prints a trace line before delegating."""
        def __init__(self, inner: LogHandler):
            super().__init__(inner.name)
            self._inner = inner
            self._next  = inner._next

        def handle(self, message: LogMessage) -> None:
            will_process = (
                (self._inner.name == "DebugHandler"   and message.level == LogLevel.DEBUG)   or
                (self._inner.name == "InfoHandler"    and message.level == LogLevel.INFO)    or
                (self._inner.name == "WarningHandler" and message.level == LogLevel.WARNING) or
                (self._inner.name == "ErrorHandler"   and message.level == LogLevel.ERROR)
            )
            action = "processing" if will_process else "passing along"
            print(f"  [{self._inner.name}] received {message.level.name} — {action}")
            self._inner.handle(message)

    # A simpler approach: just add trace prints directly inside each handler's
    # handle() method. The TracingHandler above is one way; another is to
    # modify the base class handle() to print before delegating.
    #
    # Simplest Part B solution — modify _pass_along:

    class TracedLogHandler(LogHandler, ABC):
        def _pass_along(self, message: LogMessage) -> None:
            if self._next is not None:
                print(f"  [{self.name}] received {message.level.name} — passing along")
                self._next.handle(message)

    class TDebugHandler(TracedLogHandler):
        def __init__(self): super().__init__("DebugHandler")
        def handle(self, message: LogMessage) -> None:
            if message.level == LogLevel.DEBUG:
                print(f"  [{self.name}] received {message.level.name} — processing")
                print(f"[DEBUG] {message.text}")
            else:
                self._pass_along(message)

    class TInfoHandler(TracedLogHandler):
        def __init__(self): super().__init__("InfoHandler")
        def handle(self, message: LogMessage) -> None:
            if message.level == LogLevel.INFO:
                print(f"  [{self.name}] received {message.level.name} — processing")
                print(f"[INFO]  {message.text}")
            else:
                self._pass_along(message)

    class TWarningHandler(TracedLogHandler):
        def __init__(self): super().__init__("WarningHandler")
        def handle(self, message: LogMessage) -> None:
            if message.level == LogLevel.WARNING:
                print(f"  [{self.name}] received {message.level.name} — processing")
                print(f"[WARN]  {message.text}")
            else:
                self._pass_along(message)

    class TErrorHandler(TracedLogHandler):
        def __init__(self): super().__init__("ErrorHandler")
        def handle(self, message: LogMessage) -> None:
            if message.level == LogLevel.ERROR:
                print(f"  [{self.name}] received {message.level.name} — processing")
                print(f"[ERROR] {message.text}")
            else:
                self._pass_along(message)

    td = TDebugHandler()
    ti = TInfoHandler()
    tw = TWarningHandler()
    te = TErrorHandler()
    td.set_next(ti).set_next(tw).set_next(te)

    td.handle(LogMessage(LogLevel.WARNING, "disk usage at 80%"))
