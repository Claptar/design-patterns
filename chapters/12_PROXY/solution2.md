---
layout: default
title: "Solution 2: Protection Proxy"
---

# Solution 2: Protection Proxy

## The solution

```python
ALLOWED_METHODS = {
    "viewer":  {"get_metadata"},
    "analyst": {"get_metadata", "get_content"},
    "admin":   {"get_metadata", "get_content", "delete_report"},
}


class ProtectedReportProxy(ReportService):
    def __init__(self, service: ReportService, role: str):
        self._service = service
        self._role = role

    def _check(self, method_name: str) -> None:
        allowed = ALLOWED_METHODS.get(self._role, set())
        if method_name not in allowed:
            raise PermissionError(
                f"Role '{self._role}' is not allowed to call '{method_name}'."
            )

    def get_metadata(self) -> ReportMetadata:
        self._check("get_metadata")
        return self._service.get_metadata()

    def get_content(self) -> str:
        self._check("get_content")
        return self._service.get_content()

    def delete_report(self) -> None:
        self._check("delete_report")
        self._service.delete_report()
```

## What is happening

`_check()` is the single location of all permission logic. It looks up the
role in `ALLOWED_METHODS` and raises `PermissionError` if the method is not
permitted. Using `.get(self._role, set())` means an unknown role receives an
empty allowed set, so every call raises `PermissionError` without any special
case.

Each public method calls `_check("method_name")` before forwarding. This keeps
the forwarding code clean and the permission logic in one place. If the rules
change — adding a new role or adjusting what a role can do — only `ALLOWED_METHODS`
needs updating, not the individual methods.

The wrapped service can be any `ReportService`. The proxy does not care whether
it wraps a `RealReportService` or another proxy. This will matter in Exercise 3.

## The `_check()` helper

The helper is more important than it might appear. A common mistake is to check
permissions inline in each method:

```python
def get_content(self) -> str:
    if self._role not in {"analyst", "admin"}:   # duplicated rule
        raise PermissionError(...)
    return self._service.get_content()

def delete_report(self) -> None:
    if self._role != "admin":                     # duplicated rule
        raise PermissionError(...)
    self._service.delete_report()
```

This scatters the access rules across methods. Adding a new method means
remembering to add a check. Changing who can call `get_content()` means
hunting for the right `if` block. The `_check()` helper avoids all of that.

## What the `RealReportService` does not know

`RealReportService` has no permission-checking code. It does not know what role
is calling it. If you call its methods directly, it will execute them for
anyone.

The proxy is what enforces the rules. This is the protection proxy's purpose:
the real object stays simple and focused on its job; the proxy adds a layer of
control around it.

This also makes testing easier. You can test the real service's behaviour
independently of the permission rules, and you can test the permission rules
independently of the real service's behaviour.

## Possible pitfalls

**Hardcoding role checks in each method.** Covered above. Use the lookup table.

**Using `if role == "admin" or role == "analyst"` in `_check()`.** This is
equivalent to looking up the set, but it duplicates the role membership
information that already lives in `ALLOWED_METHODS`.

**Forgetting unknown roles.** `.get(self._role, set())` handles unknown roles
without an extra branch. If you use `ALLOWED_METHODS[self._role]` instead, a
`KeyError` is raised for unknown roles, which is a less informative error than
`PermissionError`.

## Improvement ideas

**Returning the error message to the caller without leaking internals.** The
current error message says which role was denied which method. In some systems
you may want a generic "Access denied" message to avoid leaking information
about what methods exist or what roles are valid.

**Logging denied attempts.** A protection proxy is a natural place to log
unauthorised access attempts:

```python
def _check(self, method_name: str) -> None:
    allowed = ALLOWED_METHODS.get(self._role, set())
    if method_name not in allowed:
        logger.warning(
            "Denied: role=%r method=%r", self._role, method_name
        )
        raise PermissionError(...)
```

**Making the rules configurable.** `ALLOWED_METHODS` is defined at module level
here. For a larger system, the proxy could accept the rules as a constructor
argument, making it easier to test different rule sets and swap them at runtime.

```python
class ProtectedReportProxy(ReportService):
    def __init__(self, service, role, allowed_methods=None):
        self._service = service
        self._role = role
        self._rules = allowed_methods or ALLOWED_METHODS
```

---

[Exercise 1: Virtual Proxy](exercise1.md) · [Exercise 3: Caching Proxy](exercise3.md)
