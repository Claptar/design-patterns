---
layout: default
title: "Facade Exercise 3: Solution"
---

# Facade Exercise 3: Solution

## The solution

```python
class ReportFacade:
    def __init__(self, data_fetcher, formatter, emailer,
                 kpi_fetcher=None, archiver=None):
        self._data_fetcher = data_fetcher
        self._formatter = formatter
        self._emailer = emailer
        self._kpi_fetcher = kpi_fetcher
        self._archiver = archiver

    def send_weekly_report(self, recipients): ...
    def send_monthly_executive_summary(self, recipients, archive_filename): ...


class SchedulingFacade:
    def __init__(self, scheduler):
        self._scheduler = scheduler

    def schedule_report(self, report_type, cron_expr, recipients):
        return self._scheduler.schedule(report_type, cron_expr, recipients)

    def cancel_scheduled_report(self, schedule_id):
        self._scheduler.cancel(schedule_id)

    def get_schedule_status(self, schedule_id):
        return self._scheduler.status(schedule_id)


class RecipientGroupFacade:
    def __init__(self, group_store):
        self._store = group_store

    def add_recipient_group(self, group_name, emails):
        self._store.add(group_name, emails)

    def remove_recipient_group(self, group_name):
        self._store.remove(group_name)

    def list_recipient_groups(self):
        return self._store.list_all()


class ReportingPlatformFacade:
    def __init__(self, report_facade, scheduling_facade, recipient_facade):
        self._reports = report_facade
        self._scheduling = scheduling_facade
        self._recipients = recipient_facade

    def send_weekly_report(self, recipients):
        self._reports.send_weekly_report(recipients)

    def schedule_report(self, report_type, cron_expr, recipients):
        return self._scheduling.schedule_report(report_type, cron_expr, recipients)

    def add_recipient_group(self, group_name, emails):
        self._recipients.add_recipient_group(group_name, emails)

    # ... and so on for every method
```

---

## Discussion

### Recognizing the god object

The sign that `ReportFacade` had become a god object was not its size alone
— it was that its methods served three unrelated concerns. The tell is when
you find yourself asking:

> "Why would the checkout controller need to know about recipient groups?"

If the answer is "it wouldn't, but they're on the same Facade", then the
concerns are wrong. A controller that only manages scheduled reports should
be able to depend on `SchedulingFacade` alone, with no import of anything
related to report formatting or recipient lists.

The test `test_recipient_facade_usable_without_report_dependencies`
captures this exactly: instantiating `RecipientGroupFacade` requires zero
knowledge of `SalesDataFetcher`, `ReportFormatter`, or any delivery class.

### The platform Facade composes, never reimplements

The key constraint in the exercise was:

> `ReportingPlatformFacade` must delegate to the focused Facades — it must
> not re-implement any logic itself.

Every method on the platform Facade is a single delegation call:

```python
def send_weekly_report(self, recipients):
    self._reports.send_weekly_report(recipients)

def schedule_report(self, report_type, cron_expr, recipients):
    return self._scheduling.schedule_report(report_type, cron_expr, recipients)
```

There is no data manipulation, no error handling, no orchestration — just
forwarding. The platform Facade is a convenience entry point, not a new place
where logic lives. If logic appeared here, any bug fix would need to happen
in two places: the focused Facade and the platform Facade.

### This is a Facade of Facades

`ReportingPlatformFacade` is itself a Facade — but its "subsystem" is the
three focused Facades rather than raw infrastructure classes. The pattern
composes cleanly at multiple levels:

```text
infrastructure (databases, email APIs, schedulers)
    wrapped by
focused Facades (ReportFacade, SchedulingFacade, RecipientGroupFacade)
    wrapped by
platform Facade (ReportingPlatformFacade)
```

Callers can depend on whichever level is appropriate for their needs.

### The Interface Segregation Principle in action

The three focused Facades are a direct expression of ISP:

> Code should not be forced to depend on methods it does not use.

A cron job that only cancels stale schedules should depend on
`SchedulingFacade`. An admin UI that only manages recipient lists should
depend on `RecipientGroupFacade`. Neither should import the report delivery
subsystem just because it shares a Facade with it.

ISP is usually discussed in terms of interfaces and abstract base classes,
but the same principle applies to concrete classes that are used as
dependency injection targets.

---

## Possible improvements

### Abstract base classes or protocols

In a production codebase, each Facade might be backed by an abstract
interface:

```python
from abc import ABC, abstractmethod

class ReportDeliveryPort(ABC):
    @abstractmethod
    def send_weekly_report(self, recipients: list[str]) -> None: ...

    @abstractmethod
    def send_monthly_executive_summary(
        self, recipients: list[str], archive_filename: str
    ) -> None: ...


class ReportFacade(ReportDeliveryPort):
    ...
```

This lets tests substitute a fake without subclassing the real Facade:

```python
class FakeReportDelivery(ReportDeliveryPort):
    def __init__(self):
        self.deliveries = []

    def send_weekly_report(self, recipients):
        self.deliveries.append(("weekly", recipients))

    def send_monthly_executive_summary(self, recipients, archive_filename):
        self.deliveries.append(("monthly", recipients, archive_filename))
```

### Factory or builder for the platform Facade

Assembling `ReportingPlatformFacade` with all its dependencies can become
verbose. A factory function or builder cleans this up at the application
boundary:

```python
def build_reporting_platform(config) -> ReportingPlatformFacade:
    return ReportingPlatformFacade(
        report_facade=ReportFacade(
            data_fetcher=SalesDataFetcher(config.db_url),
            formatter=ReportFormatter(),
            emailer=ReportEmailer(config.smtp_host),
            kpi_fetcher=KpiFetcher(config.db_url),
            archiver=ReportArchiver(config.archive_path),
        ),
        scheduling_facade=SchedulingFacade(
            scheduler=ReportScheduler(config.db_url),
        ),
        recipient_facade=RecipientGroupFacade(
            group_store=RecipientGroupStore(config.db_url),
        ),
    )
```

This is the Facade and Factory patterns working together: Factory wires up
the platform, Facade hides the platform's complexity from callers.

---

[Back to Facade](facade.md)
