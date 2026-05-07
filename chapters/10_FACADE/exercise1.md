---
layout: default
title: "Facade Exercise 1: Basic Report Facade"
---

# Facade Exercise 1: Basic Report Facade

## Goal

Practice building a basic Facade that coordinates several subsystem components
behind one clean entry point.

---

## Scenario

You are building a reporting tool for a small analytics company.

The tool needs to generate and deliver a weekly sales report. The process
involves three steps:

1. Fetch the sales data from a data store.
2. Format the data into a human-readable report string.
3. Email the report to a list of recipients.

The subsystem classes already exist and work correctly. They are defined
in `exercise1.py`. Your job is to build the `ReportFacade` that hides
their coordination from callers.

---

## What you need to build

Implement the `ReportFacade` class so that this usage works:

```python
facade = ReportFacade(
    data_fetcher=SalesDataFetcher(),
    formatter=ReportFormatter(),
    emailer=ReportEmailer(),
)

facade.send_weekly_report(recipients=["alice@example.com", "bob@example.com"])
```

The Facade should:

- Call `data_fetcher.fetch_weekly_sales()` to get the data.
- Pass the data to `formatter.format(data)` to produce a report string.
- Pass the report string and recipients to `emailer.send(report, recipients)`.

The caller should not need to know about any of the subsystem classes or
the order in which they are called.

---

## Constraints

- Do not modify any of the existing subsystem classes.
- `ReportFacade.__init__` should accept the three subsystem objects as
  constructor arguments (dependency injection).
- The method on the Facade should be named `send_weekly_report`.

---

## File to edit

`exercise1.py`

Run the tests with:

```bash
python -m pytest exercise1.py -v
```
