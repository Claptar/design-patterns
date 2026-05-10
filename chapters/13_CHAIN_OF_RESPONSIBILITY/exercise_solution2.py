"""
Exercise 2 — Solution: Suppress and Flexible Pipelines
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


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
# Part A
# ---------------------------------------------------------------------------

class SuppressHandler(LogHandler):
    def __init__(self, suppress_up_to: LogLevel):
        super().__init__("SuppressHandler")
        self._suppress_up_to = suppress_up_to

    def handle(self, message: LogMessage) -> None:
        if message.level.value <= self._suppress_up_to.value:
            return          # silently drop
        self._pass_along(message)


# ---------------------------------------------------------------------------
# Part B
# ---------------------------------------------------------------------------

class FallbackHandler(LogHandler):
    def __init__(self):
        super().__init__("FallbackHandler")

    def handle(self, message: LogMessage) -> None:
        print(f"[FALLBACK] {message.level.name}: {message.text}")


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
    assert out.strip() == ""


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
    production = SuppressHandler(LogLevel.DEBUG)
    production.set_next(InfoHandler()).set_next(WarningHandler()).set_next(ErrorHandler())

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
    suppress.set_next(WarningHandler()).set_next(ErrorHandler())

    for msg in [
        LogMessage(LogLevel.DEBUG,   "ignored"),
        LogMessage(LogLevel.INFO,    "ignored"),
        LogMessage(LogLevel.WARNING, "disk usage at 80%"),
        LogMessage(LogLevel.ERROR,   "database connection failed"),
    ]:
        suppress.handle(msg)

    print("\n=== Part B: fallback catches unhandled ===")
    debug = DebugHandler()
    debug.set_next(InfoHandler()).set_next(FallbackHandler())

    for msg in [
        LogMessage(LogLevel.DEBUG,   "hello"),
        LogMessage(LogLevel.INFO,    "login"),
        LogMessage(LogLevel.WARNING, "nobody handles this"),
        LogMessage(LogLevel.ERROR,   "nobody handles this either"),
    ]:
        debug.handle(msg)

    print("\n=== Part C: two independent pipelines ===")
    prod = SuppressHandler(LogLevel.DEBUG)
    prod.set_next(InfoHandler()).set_next(WarningHandler()).set_next(ErrorHandler())

    dev2 = DebugHandler()
    dev2.set_next(InfoHandler()).set_next(WarningHandler()).set_next(ErrorHandler()).set_next(FallbackHandler())

    messages = [
        LogMessage(LogLevel.DEBUG,   "startup"),
        LogMessage(LogLevel.INFO,    "user logged in"),
        LogMessage(LogLevel.WARNING, "high memory"),
        LogMessage(LogLevel.ERROR,   "crash"),
    ]

    print("\n-- Production --")
    for m in messages:
        prod.handle(m)

    print("\n-- Development --")
    for m in messages:
        dev2.handle(m)
