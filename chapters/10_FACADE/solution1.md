---
layout: default
title: "Facade Exercise 1: Solution"
---

# Facade Exercise 1: Solution

## The solution

```python
class ReportFacade:
    def __init__(self, data_fetcher, formatter, emailer):
        self._data_fetcher = data_fetcher
        self._formatter = formatter
        self._emailer = emailer

    def send_weekly_report(self, recipients: list[str]) -> None:
        data = self._data_fetcher.fetch_weekly_sales()
        report = self._formatter.format(data)
        self._emailer.send(report, recipients)
```

Three lines in the method body. That is all a basic Facade needs to do.

---

## What makes this a Facade

The caller goes from this:

```python
fetcher = SalesDataFetcher()
formatter = ReportFormatter()
emailer = ReportEmailer()

data = fetcher.fetch_weekly_sales()
report = formatter.format(data)
emailer.send(report, recipients)
```

To this:

```python
facade.send_weekly_report(recipients)
```

The caller no longer needs to know:

- that fetching comes before formatting
- that formatting produces a string that the emailer expects
- that three separate objects are involved at all

That is the core value of Facade: the orchestration lives in one place instead
of leaking into every caller.

---

## Why dependency injection matters here

The constructor takes the subsystem objects rather than creating them:

```python
def __init__(self, data_fetcher, formatter, emailer):
    self._data_fetcher = data_fetcher
    ...
```

This is the **Dependency Inversion Principle** in action. Because the Facade
receives its dependencies from outside, a test can pass in fakes:

```python
class FakeEmailer:
    def __init__(self):
        self.sent = []

    def send(self, report, recipients):
        self.sent.extend(recipients)

emailer = FakeEmailer()
facade = ReportFacade(SalesDataFetcher(), ReportFormatter(), emailer)
facade.send_weekly_report(["alice@example.com"])

assert len(emailer.sent) == 1
```

If the Facade had created `ReportEmailer()` internally, the test would send
a real email. Dependency injection keeps the Facade testable.

---

## Common mistake: putting logic in the wrong place

A tempting mistake is to put orchestration logic in the caller:

```python
# caller code — this is the smell
data = facade.fetch_data()
report = facade.format(report)
facade.email(report, recipients)
```

This is not a Facade — it is just wrapping individual subsystem calls behind
a thin proxy. The caller still controls the ordering. The key signal that you
have a real Facade is that the caller makes one call and gets the outcome,
with no intermediate steps visible.

---

## Next

[Exercise 2: Multiple report types and error handling](exercise2.md)
