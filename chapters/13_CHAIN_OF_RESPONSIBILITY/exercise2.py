"""
Exercise 2: Method Chain — Suppress and Flexible Pipelines

Build on the logging pipeline from Exercise 1.
Add SuppressHandler and FallbackHandler, then compose different pipelines.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


# ---------------------------------------------------------------------------
# Copy-paste base from Exercise 1 (already working)
# ---------------------------------------------------------------------------

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
    def __init__(self): super().__init__("DebugHandler")
    def handle(self, message: LogMessage) -> None:
        if message.level == LogLevel.DEBUG:
            print(f"[DEBUG] {message.text}")
        else:
            self._pass_along(message)


class InfoHandler(LogHandler):
    def __init__(self): super().__init__("InfoHandler")
    def handle(self, message: LogMessage) -> None:
        if message.level == LogLevel.INFO:
            print(f"[INFO]  {message.text}")
        else:
            self._pass_along(message)


class WarningHandler(LogHandler):
    def __init__(self): super().__init__("WarningHandler")
    def handle(self, message: LogMessage) -> None:
        if message.level == LogLevel.WARNING:
            print(f"[WARN]  {message.text}")
        else:
            self._pass_along(message)


class ErrorHandler(LogHandler):
    def __init__(self): super().__init__("ErrorHandler")
    def handle(self, message: LogMessage) -> None:
        if message.level == LogLevel.ERROR:
            print(f"[ERROR] {message.text}")
        else:
            self._pass_along(message)


# ---------------------------------------------------------------------------
# Part A — implement SuppressHandler
# ---------------------------------------------------------------------------

class SuppressHandler(LogHandler):
    """
    Silently drops any message whose level is <= suppress_up_to.
    Messages above that level are passed to the next handler.
    """

    def __init__(self, suppress_up_to: LogLevel):
        super().__init__("SuppressHandler")
        self._suppress_up_to = suppress_up_to

    def handle(self, message: LogMessage) -> None:
        # TODO: if message level <= self._suppress_up_to, return silently.
        #       Otherwise pass along.
        ...


# ---------------------------------------------------------------------------
# Part B — implement FallbackHandler
# ---------------------------------------------------------------------------

class FallbackHandler(LogHandler):
    """
    Catches any message that no earlier handler processed.
    Prints: [FALLBACK] {level_name}: {text}
    """

    def __init__(self):
        super().__init__("FallbackHandler")

    def handle(self, message: LogMessage) -> None:
        # TODO: print the fallback line. No level check needed — it handles everything.
        ...


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_suppress_drops_low_levels(capsys):
    suppress = SuppressHandler(LogLevel.INFO)
    warning  = WarningHandler()
    error    = ErrorHandler()
    suppress.set_next(warning).set_next(error)

    suppress.handle(LogMessage(LogLevel.DEBUG,   "ignored"))
    suppress.handle(LogMessage(LogLevel.INFO,    "ignored"))
    out = capsys.readouterr().out
    assert out.strip() == "", f"Expected no output, got: {out!r}"


def test_suppress_passes_high_levels(capsys):
    suppress = SuppressHandler(LogLevel.INFO)
    warning  = WarningHandler()
    error    = ErrorHandler()
    suppress.set_next(warning).set_next(error)

    suppress.handle(LogMessage(LogLevel.WARNING, "printed"))
    suppress.handle(LogMessage(LogLevel.ERROR,   "also printed"))
    out = capsys.readouterr().out
    assert "[WARN]"  in out
    assert "[ERROR]" in out


def test_fallback_catches_unhandled(capsys):
    debug    = DebugHandler()
    info     = InfoHandler()
    fallback = FallbackHandler()
    debug.set_next(info).set_next(fallback)

    # WARNING has no handler — should reach fallback
    debug.handle(LogMessage(LogLevel.WARNING, "disk usage at 80%"))
    out = capsys.readouterr().out
    assert "[FALLBACK]" in out
    assert "disk usage at 80%" in out


def test_fallback_not_reached_when_handler_exists(capsys):
    warning  = WarningHandler()
    fallback = FallbackHandler()
    warning.set_next(fallback)

    warning.handle(LogMessage(LogLevel.WARNING, "handled"))
    out = capsys.readouterr().out
    assert "[WARN]"     in out
    assert "[FALLBACK]" not in out


def test_two_independent_pipelines(capsys):
    # Production: suppress debug
    production = SuppressHandler(LogLevel.DEBUG)
    production.set_next(InfoHandler()).set_next(WarningHandler()).set_next(ErrorHandler())

    # Dev: everything through, fallback at end
    dev = DebugHandler()
    dev.set_next(InfoHandler()).set_next(WarningHandler()).set_next(ErrorHandler()).set_next(FallbackHandler())

    production.handle(LogMessage(LogLevel.DEBUG, "prod debug"))
    prod_out = capsys.readouterr().out
    assert prod_out.strip() == ""

    dev.handle(LogMessage(LogLevel.DEBUG, "dev debug"))
    dev_out = capsys.readouterr().out
    assert "[DEBUG]" in dev_out


if __name__ == "__main__":
    print("=== Part A: suppress up to INFO ===")
    suppress = SuppressHandler(LogLevel.INFO)
    warning  = WarningHandler()
    error    = ErrorHandler()
    suppress.set_next(warning).set_next(error)

    suppress.handle(LogMessage(LogLevel.DEBUG,   "ignored"))
    suppress.handle(LogMessage(LogLevel.INFO,    "ignored"))
    suppress.handle(LogMessage(LogLevel.WARNING, "disk usage at 80%"))
    suppress.handle(LogMessage(LogLevel.ERROR,   "database connection failed"))

    print("\n=== Part B: fallback catches unhandled ===")
    debug    = DebugHandler()
    info     = InfoHandler()
    fallback = FallbackHandler()
    debug.set_next(info).set_next(fallback)

    debug.handle(LogMessage(LogLevel.DEBUG,   "hello"))
    debug.handle(LogMessage(LogLevel.INFO,    "login"))
    debug.handle(LogMessage(LogLevel.WARNING, "nobody handles this"))
    debug.handle(LogMessage(LogLevel.ERROR,   "nobody handles this either"))
