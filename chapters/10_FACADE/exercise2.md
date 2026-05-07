---
layout: default
title: "Facade Exercise 2: Multiple Report Types and Error Handling"
---

# Facade Exercise 2: Multiple Report Types and Error Handling

## Goal

Practice two things that arise naturally as a Facade grows:

1. The Facade exposes **multiple operations** with different orchestration paths.
2. The Facade owns **error handling and cleanup** so callers never see
   half-completed operations.

---

## Scenario

The reporting tool from Exercise 1 has grown. The company now needs two kinds
of reports: the existing weekly sales report and a new monthly executive
summary.

The monthly summary has a different flow:

1. Fetch sales data for the full month (`data_fetcher.fetch_monthly_sales()`).
2. Fetch the KPI snapshot (`kpi_fetcher.fetch_kpis()`).
3. Format both into a combined summary (`formatter.format_executive(data, kpis)`).
4. Save the report to a file archive before emailing
   (`archiver.save(report, filename)`).
5. Email it to the board (`emailer.send(report, recipients)`).

There is also a new error requirement: if the archiver fails (raises
`ArchiveError`), the email must **not** be sent. The caller should receive a
clean `ReportDeliveryError` instead of a raw `ArchiveError`. The caller
should never have to handle subsystem-specific exceptions.

---

## What you need to build

Extend `ReportFacade` with a second method:

```python
facade.send_monthly_executive_summary(
    recipients=["board@example.com"],
    archive_filename="executive_2024_10.txt",
)
```

And wrap errors so that:

```python
try:
    facade.send_monthly_executive_summary(
        recipients=["board@example.com"],
        archive_filename="executive_2024_10.txt",
    )
except ReportDeliveryError as e:
    print(f"Delivery failed: {e}")
```

Never leaks `ArchiveError` to the caller.

---

## New subsystem classes provided

The exercise file adds:

- `KpiFetcher` — has `fetch_kpis() -> dict`
- `ReportArchiver` — has `save(report: str, filename: str) -> None`; may raise `ArchiveError`
- `ArchiveError` — exception raised by the archiver on failure
- `ReportDeliveryError` — the exception your Facade should raise to callers

The existing `SalesDataFetcher`, `ReportFormatter`, and `ReportEmailer` are
extended with the new methods needed.

---

## Constraints

- `ReportFacade.__init__` now also accepts `kpi_fetcher` and `archiver`.
- Do not let `ArchiveError` propagate out of the Facade.
- If archiving fails, do not send the email.
- Raise `ReportDeliveryError` (with a descriptive message) when archiving fails.

---

## File to edit

`exercise2.py`

Run the tests with:

```bash
python -m pytest exercise2.py -v
```
