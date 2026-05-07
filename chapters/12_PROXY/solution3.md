---
layout: default
title: "Solution 3: Caching Proxy and Proxy Composition"
---

# Solution 3: Caching Proxy and Proxy Composition

## Part A: the caching proxy

```python
class CachingReportProxy(ReportService):
    def __init__(self, service: ReportService):
        self._service = service
        self._cached_content: str | None = None

    def get_metadata(self) -> ReportMetadata:
        return self._service.get_metadata()

    def get_content(self) -> str:
        if self._cached_content is None:
            self._cached_content = self._service.get_content()
        return self._cached_content

    def delete_report(self) -> None:
        self._service.delete_report()
        self._cached_content = None
```

## Part B: composition

```python
def build_report_service(
    report_id: str,
    title: str,
    author: str,
    role: str,
) -> ReportService:
    real = RealReportService(report_id, title, author)
    cached = CachingReportProxy(real)
    protected = ProtectedReportProxy(cached, role)
    return protected
```

## What is happening

### The cache

`_cached_content` starts as `None`. On the first `get_content()` call, the
proxy forwards to the inner service, stores the result, and returns it. On
every subsequent call the guard fires immediately and returns the stored value.
No forwarding happens.

`delete_report()` forwards to the real service and then clears the cache by
setting `_cached_content = None` again. This means the next `get_content()`
call will regenerate — which is correct, because the report has just been
deleted.

`get_metadata()` does not cache. Metadata is cheap. It also avoids the question
of whether cached metadata would become stale after a delete.

### The composition

The composed object looks like this from the inside out:

```
ProtectedReportProxy (role check)
  └── CachingReportProxy (cache)
        └── RealReportService (generation)
```

Every call enters at the top of this stack. The protection proxy checks
permissions first. If the call is allowed, it forwards to the caching proxy.
The caching proxy checks its cache. If there is a hit, it returns immediately.
If not, it forwards to the real service.

The caller holds a reference typed as `ReportService`. It cannot see the stack.
It just calls methods.

### Why the order matters

Putting the caching proxy outside the protection proxy would create a security
hole. Suppose an admin populates the cache, and then a viewer calls
`get_content()`. If caching is outermost:

```
CachingProxy.get_content()
    → cache hit → returns content to viewer, no permission check reached
```

The viewer gets the content without ever being checked. That is wrong.

With protection outermost:

```
ProtectedProxy.get_content()
    → role is "viewer", denied → PermissionError raised
```

The caching layer is never reached. The protection proxy always runs first
regardless of cache state.

This is a general rule for stacking proxies: **put the cheapest, most
restrictive check outermost**. That way, rejected calls are stopped as early
as possible and do not waste work.

## What each proxy owns

| Proxy | Responsibility |
|---|---|
| `ProtectedReportProxy` | Access control |
| `CachingReportProxy` | Performance |
| `RealReportService` | Business logic |

None of these knows about the others' concerns. `RealReportService` has no
caching code and no permission-checking code. `CachingReportProxy` has no
permission-checking code and no report-generation code. `ProtectedReportProxy`
has no caching code and no report-generation code.

Each class has one reason to change:

- Access rules change → update `ProtectedReportProxy` (or `ALLOWED_METHODS`).
- Cache strategy changes → update `CachingReportProxy`.
- Report format changes → update `RealReportService`.

## Possible pitfalls

**Clearing the cache in the wrong place.** If `_cached_content = None` is set
before forwarding `delete_report()`, and the forward raises an exception, the
cache is cleared even though the delete failed. Setting it after the forward is
safer.

**Sharing a cache across instances.** If `_cached_content` were a class
attribute instead of an instance attribute, all proxies would share the same
cache. That would mean one report's content being returned for a completely
different report. Always use instance attributes for per-proxy state.

**Not composing at all.** It is tempting to add caching logic directly inside
`ProtectedReportProxy` or permission-checking directly inside
`CachingReportProxy`. That is the path back to one big class with multiple
reasons to change. The composition approach keeps concerns separate and each
proxy reusable independently.

## Improvement ideas

**Cache expiry.** The current cache never expires. In a real system you might
want to expire the cache after a timeout:

```python
import time

def get_content(self) -> str:
    now = time.monotonic()
    if self._cached_content is None or now - self._cached_at > self._ttl:
        self._cached_content = self._service.get_content()
        self._cached_at = now
    return self._cached_content
```

**A factory that returns a `ReportService` protocol.** In production code,
`build_report_service` would often be part of a dependency-injection container
or a factory class, keeping the composition logic in one place for the whole
application.

**Logging proxy added to the stack.** Because every proxy wraps a `ReportService`,
you could add a fourth layer without touching any of the existing three:

```python
logged = LoggingReportProxy(protected, user_id=current_user.id)
```

The stack grows by one line. No existing code changes.

---

[Exercise 2: Protection Proxy](exercise2.md)
