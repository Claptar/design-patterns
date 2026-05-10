"""
Exercise 1: Method Chain — Logging Pipeline

Build a logging pipeline using the Chain of Responsibility method chain pattern.

Part A: implement the chain so that each handler processes messages at its own
        level and passes the rest along.

Part B: add trace output so you can see every handler's decision.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto


# ---------------------------------------------------------------------------
# Log level
# ---------------------------------------------------------------------------

class LogLevel(Enum):
    DEBUG   = 1
    INFO    = 2
    WARNING = 3
    ERROR   = 4


# ---------------------------------------------------------------------------
# Log message
# ---------------------------------------------------------------------------

@dataclass
class LogMessage:
    level: LogLevel
    text: str


# ---------------------------------------------------------------------------
# Abstract handler
# ---------------------------------------------------------------------------

class LogHandler(ABC):
    def __init__(self, name: str):
        self.name = name
        self._next: LogHandler | None = None

    def set_next(self, handler: LogHandler) -> LogHandler:
        """Wire the next handler. Returns handler so calls can be chained."""
        # TODO: store handler as self._next and return it
        ...

    @abstractmethod
    def handle(self, message: LogMessage) -> None:
        """Process or pass along the message."""
        ...

    def _pass_along(self, message: LogMessage) -> None:
        """Helper: forward to next handler if one exists."""
        # TODO: call self._next.handle(message) if self._next is not None
        ...


# ---------------------------------------------------------------------------
# Concrete handlers
# ---------------------------------------------------------------------------

class DebugHandler(LogHandler):
    def __init__(self):
        super().__init__("DebugHandler")

    def handle(self, message: LogMessage) -> None:
        # TODO: if message.level is DEBUG, print formatted output and stop.
        #       Otherwise pass along.
        # Formatted output: "[DEBUG] {message.text}"
        ...


class InfoHandler(LogHandler):
    def __init__(self):
        super().__init__("InfoHandler")

    def handle(self, message: LogMessage) -> None:
        # TODO: if message.level is INFO, print "[INFO]  {message.text}"
        #       Otherwise pass along.
        ...


class WarningHandler(LogHandler):
    def __init__(self):
        super().__init__("WarningHandler")

    def handle(self, message: LogMessage) -> None:
        # TODO: if message.level is WARNING, print "[WARN]  {message.text}"
        #       Otherwise pass along.
        ...


class ErrorHandler(LogHandler):
    def __init__(self):
        super().__init__("ErrorHandler")

    def handle(self, message: LogMessage) -> None:
        # TODO: if message.level is ERROR, print "[ERROR] {message.text}"
        #       Otherwise pass along.
        ...


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def build_chain() -> LogHandler:
    """Wire up the full chain and return the entry point."""
    debug   = DebugHandler()
    info    = InfoHandler()
    warning = WarningHandler()
    error   = ErrorHandler()
    # TODO: wire the chain and return the entry point
    ...


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
    # Only one line should be printed — INFO handled it, others passed
    assert len(lines) == 1
    assert "[INFO]" in lines[0]


def test_unknown_level_dropped_silently(capsys):
    """A message whose level no handler claims produces no output."""
    # Simulate by creating a chain without ErrorHandler and sending ERROR
    debug   = DebugHandler()
    info    = InfoHandler()
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
