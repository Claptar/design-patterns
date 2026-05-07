---
layout: default
title: "Facade Exercise 2: Solution"
---

# Facade Exercise 2: Solution

## The solution

```python
class ReportFacade:
    def __init__(
        self,
        data_fetcher,
        formatter,
        emailer,
        kpi_fetcher=None,
        archiver=None,
    ):
        self._data_fetcher = data_fetcher
        self._formatter = formatter
        self._emailer = emailer
        self._kpi_fetcher = kpi_fetcher
        self._archiver = archiver

    def send_weekly_report(self, recipients: list[str]) -> None:
        data = self._data_fetcher.fetch_weekly_sales()
        report = self._formatter.format(data)
        self._emailer.send(report, recipients)

    def send_monthly_executive_summary(
        self,
        recipients: list[str],
        archive_filename: str,
    ) -> None:
        data = self._data_fetcher.fetch_monthly_sales()
        kpis = self._kpi_fetcher.fetch_kpis()
        report = self._formatter.format_executive(data, kpis)

        try:
            self._archiver.save(report, archive_filename)
        except ArchiveError as e:
            raise ReportDeliveryError(
                f"Could not archive report before sending: {e}"
            ) from e

        self._emailer.send(report, recipients)
```

---

## Discussion

### Error translation is a Facade responsibility

The most important thing to notice in this solution is what happens to
`ArchiveError`:

```python
try:
    self._archiver.save(report, archive_filename)
except ArchiveError as e:
    raise ReportDeliveryError(
        f"Could not archive report before sending: {e}"
    ) from e
```

The caller should not need to know that the system uses a `ReportArchiver`
internally, or that the archiver raises `ArchiveError`. If we let
`ArchiveError` escape the Facade, every caller has to import it and handle it.
That means callers are now coupled to a subsystem class they should not even
know about.

The rule is: **exceptions that come from subsystem internals belong inside
the Facade**. The Facade translates them into domain-level errors that callers
can actually reason about — in this case, `ReportDeliveryError`.

The `raise ... from e` part preserves the original traceback for debugging,
while still presenting the clean interface.

### The email must not be sent if archiving fails

Notice that the email line comes *after* the try/except block:

```python
        try:
            self._archiver.save(report, archive_filename)
        except ArchiveError as e:
            raise ReportDeliveryError(...) from e

        self._emailer.send(report, recipients)   # only reached if no exception
```

If the archiver raises, we raise `ReportDeliveryError` immediately, and
`self._emailer.send(...)` is never reached. This is correct because the
company requires the report to be archived before it is distributed.

A common mistake is to wrap both calls in the same try/except, which loses
control of ordering:

```python
# Wrong — does not guarantee ordering
try:
    self._archiver.save(report, archive_filename)
    self._emailer.send(report, recipients)
except ArchiveError as e:
    raise ReportDeliveryError(...) from e
```

This version actually behaves the same in this case, but it is less clear
about intent. Keeping archiving and emailing as separate steps with a guard
between them communicates the ordering requirement explicitly.

### Different operations, same Facade

Both `send_weekly_report` and `send_monthly_executive_summary` live on the
same `ReportFacade`. This is appropriate because they are both about the same
domain concern — delivering reports — and share several subsystem objects.

The boundary would start to feel wrong if the Facade began growing operations
that are about different concerns: generating invoices, scheduling reminders,
managing user accounts. That is the signal to split into multiple focused
Facades — which is exactly what Exercise 3 explores.

---

## Possible improvements

### Make subsystem failures more descriptive

Right now the `ReportDeliveryError` message wraps the raw `ArchiveError`
message. In production you might want to include context:

```python
raise ReportDeliveryError(
    f"Monthly executive summary could not be archived "
    f"to '{archive_filename}': {e}"
) from e
```

### Consider a result object instead of raising

Some teams prefer returning a result object instead of raising:

```python
@dataclass
class DeliveryResult:
    success: bool
    error: str | None = None
```

That style is common in Go-influenced codebases. Either is valid — the key
point is that `ArchiveError` never escapes.

---

## Next

[Exercise 3: Avoiding the god object — splitting Facades](exercise3.md)
