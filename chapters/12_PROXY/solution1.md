---
layout: default
title: "Solution 1: Virtual Proxy"
---

# Solution 1: Virtual Proxy

## The solution

```python
class LazyReportProxy(ReportService):
    def __init__(self, report_id: str, title: str, author: str):
        self._report_id = report_id
        self._title = title
        self._author = author
        self._real: RealReportService | None = None

    def _load(self) -> RealReportService:
        if self._real is None:
            self._real = RealReportService(
                self._report_id,
                self._title,
                self._author,
            )
        return self._real

    def get_metadata(self) -> ReportMetadata:
        return ReportMetadata(
            report_id=self._report_id,
            title=self._title,
            author=self._author,
        )

    def get_content(self) -> str:
        return self._load().get_content()
```

## What is happening

The proxy stores the three constructor arguments as plain attributes. It does
not create a `RealReportService` at this point.

`get_metadata()` assembles a `ReportMetadata` from those stored attributes
directly. It never calls `_load()`. This is the key: the proxy has enough
information to answer the cheap question on its own.

`get_content()` calls `_load()`, which creates the `RealReportService` on the
first call and caches it in `self._real`. Every subsequent call to
`get_content()` reuses the same instance, so `_generate()` only runs once.

The caller holds a `ReportService` reference. It cannot tell whether the object
is a proxy or a real service. That substitutability is what makes the proxy
transparent.

## The `_load()` helper

The `_load()` pattern is the core of a virtual proxy:

```python
def _load(self):
    if self._real is None:
        self._real = ExpensiveObject(...)
    return self._real
```

It is sometimes called "lazy initialisation". The real object is created at
most once, on demand. Any method that needs the real object calls `_load()`
first. Any method that can answer without the real object skips it entirely.

## Possible pitfalls

**Putting logic in `__init__` by accident.** A common mistake is to write:

```python
def __init__(self, report_id, title, author):
    self._real = RealReportService(report_id, title, author)  # wrong
```

This creates the real service immediately and defeats the purpose of the proxy.

**Forgetting that `get_metadata()` should not call `_load()`.** Another common
mistake is to write:

```python
def get_metadata(self):
    return self._load().get_metadata()  # works, but unnecessary
```

This is correct in that it returns the right answer, but it means accessing
metadata triggers the expensive generation. In this exercise the proxy has all
the metadata it needs from the constructor. `_load()` is not required.

**Creating a new `RealReportService` on every call.** If `_load()` is not
written carefully, the guard can be missing:

```python
def _load(self):
    self._real = RealReportService(...)   # creates a new one every time
    return self._real
```

The `if self._real is None:` guard is what prevents this.

## Improvement ideas

**Thread safety.** In a multi-threaded server, two threads could both see
`self._real is None` and both create a `RealReportService`. For production
code, protect the guard with a lock:

```python
import threading

def __init__(self, ...):
    ...
    self._lock = threading.Lock()

def _load(self):
    if self._real is None:
        with self._lock:
            if self._real is None:   # double-checked locking
                self._real = RealReportService(...)
    return self._real
```

**Returning a copy of metadata.** Because `ReportMetadata` is a frozen
dataclass, returning it directly is safe. If it were mutable, you would want to
return a copy to prevent callers from modifying the proxy's internal state.

---

[Exercise 2: Protection Proxy](exercise2.md)
