---
layout: default
title: "Exercise 2: Protection Proxy"
---

# Exercise 2: Protection Proxy

## Scenario

The dashboard now has user roles. Not every role should be allowed to call every
method on the report service.

The access rules are:

| Role | `get_metadata()` | `get_content()` | `delete_report()` |
|---|---|---|---|
| `viewer` | yes | no | no |
| `analyst` | yes | yes | no |
| `admin` | yes | yes | yes |
| anything else | no | no | no |

Notice that `delete_report()` is a new method that did not exist in Exercise 1.
The subject interface has been extended to include it.

Your task is to add a **protection proxy** that enforces these rules before
forwarding any call.

## What you need to implement

Open `exercise2.py` and implement `ProtectedReportProxy`.

The proxy must:

- Wrap any `ReportService` instance and a `role` string.
- Before forwarding any call, check that the current role is allowed to make
  that call. Raise `PermissionError` with a clear message if it is not.
- Implement a single `_check(method_name)` helper that contains the permission
  logic. Do not duplicate that logic in each method.
- All three methods must be present and enforced.

The access rules are already defined for you in `ALLOWED_METHODS`.

## The interface

```python
class ReportService(ABC):
    def get_metadata(self) -> ReportMetadata: ...
    def get_content(self) -> str: ...
    def delete_report(self) -> None: ...
```

## Running the tests

```bash
pytest exercise2.py -v
```

## Hints

- `_check(method_name)` should look up the role in `ALLOWED_METHODS` and
  raise `PermissionError` if the method name is not in the allowed set.
  An unknown role should be treated the same as an empty allowed set.

- Each public method calls `_check("method_name")` first, then forwards:

```python
def get_content(self) -> str:
    self._check("get_content")
    return self._service.get_content()
```

- The proxy does not need to know what the methods do. It only needs to
  know whether the current role is allowed to call them.

## What to notice when it works

A `viewer` can read report titles but cannot download content or delete
anything. An `analyst` can read and download but cannot delete. An `admin` can
do everything. An unknown role is denied everything, including metadata.

The `RealReportService` itself has no permission-checking code. All access
control lives in the proxy.
