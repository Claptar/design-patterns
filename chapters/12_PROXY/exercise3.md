---
layout: default
title: "Exercise 3: Caching Proxy and Proxy Composition"
---

# Exercise 3: Caching Proxy and Proxy Composition

## Scenario

The same report is often requested many times in a session — by different tabs,
background refreshes, and download attempts. Each call to `get_content()` on
the real service is expensive. The content does not change between requests
unless the report is deleted and regenerated.

You need two things:

1. A **caching proxy** that remembers the result of `get_content()` and returns
   it on subsequent calls without hitting the real service again.
2. A **factory function** that composes all three proxies — virtual (from
   Exercise 1 is replaced here by the real service directly), protection, and
   caching — into a single `ReportService` that callers can use without knowing
   any of that complexity exists.

## Part A: implement `CachingReportProxy`

Open `exercise3.py` and implement `CachingReportProxy`.

The proxy must:

- Wrap any `ReportService` instance.
- On the first call to `get_content()`, forward to the wrapped service and
  store the result.
- On all subsequent calls to `get_content()`, return the stored result without
  forwarding.
- Always forward `get_metadata()` without caching.
- Always forward `delete_report()` and then clear the cache. The next call to
  `get_content()` must generate fresh content.

## Part B: implement `build_report_service()`

Implement `build_report_service(report_id, title, author, role)` so that it
returns a fully composed `ReportService` with protection and caching.

The layer order matters. Think about it before reading the hint below.

```
outer: ProtectedReportProxy
    middle: CachingReportProxy
        inner: RealReportService
```

## Running the tests

```bash
pytest exercise3.py -v
```

## Hints

**Part A — the cache.**

A single optional attribute is enough:

```python
self._cached_content: str | None = None
```

In `get_content()`:

```python
if self._cached_content is None:
    self._cached_content = self._service.get_content()
return self._cached_content
```

In `delete_report()`: forward the call, then set `self._cached_content = None`.

**Part B — why protection wraps caching, not the other way around.**

If caching were outermost, an unauthorised caller could trigger a cache population:

```
CachingProxy.get_content()
    → ProtectedProxy.get_content()    [denied]
```

The denied call raises `PermissionError`, so nothing is cached. That is fine
for this simple case. But consider this scenario: an admin calls `get_content()`
first and populates the cache. Then a viewer calls `get_content()`. If caching
is outermost, the viewer gets the cached content without ever reaching the
protection check:

```
CachingProxy.get_content()    ← cache hit, returns content to viewer
```

Putting protection outermost prevents this completely:

```
ProtectedProxy.get_content()  ← denied immediately for viewer
```

The protection proxy must be outermost so that every call is checked before
anything else happens.

## What to notice when it works

Call `get_content()` three times on the composed service with role `"analyst"`.
Only one `[RealReportService] Generating...` message appears. Call
`delete_report()` with role `"admin"`, then `get_content()` again — a second
generation message appears because the cache was cleared.
