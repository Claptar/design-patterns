---
layout: default
title: "Facade Exercise 3: Avoiding the God Object"
---

# Facade Exercise 3: Avoiding the God Object

## Goal

Practice recognizing when a Facade is becoming a god object, splitting it
into focused Facades, and wiring them together cleanly.

---

## Scenario

The reporting platform has grown significantly. The single `ReportFacade`
now has eight methods:

```text
send_weekly_report(...)
send_monthly_executive_summary(...)
schedule_report(report_type, cron_expr, recipients)
cancel_scheduled_report(schedule_id)
get_schedule_status(schedule_id)
add_recipient_group(group_name, emails)
remove_recipient_group(group_name)
list_recipient_groups()
```

The first two are report delivery. The next three are about scheduling. The
last three are about managing recipient groups — an entirely different concern.

Every controller in the system now depends on this one `ReportFacade`, even
controllers that only need to manage recipients and never send a report.

---

## What you need to build

Split the bloated `ReportFacade` into three focused Facades:

```text
ReportFacade          — send_weekly_report, send_monthly_executive_summary
SchedulingFacade      — schedule_report, cancel_scheduled_report, get_schedule_status
RecipientGroupFacade  — add_recipient_group, remove_recipient_group, list_recipient_groups
```

Each Facade should only depend on the subsystem objects it actually uses.

Additionally, build a `ReportingPlatformFacade` that composes the three
focused Facades and exposes all eight methods — for callers that genuinely
need the full platform:

```python
platform = ReportingPlatformFacade(
    report_facade=ReportFacade(...),
    scheduling_facade=SchedulingFacade(...),
    recipient_facade=RecipientGroupFacade(...),
)

# can use any method from any sub-facade
platform.send_weekly_report(recipients=["alice@example.com"])
platform.schedule_report("weekly", "0 8 * * MON", ["team@example.com"])
platform.add_recipient_group("board", ["ceo@example.com"])
```

---

## Constraints

- Each focused Facade must only accept the subsystem objects it needs.
- `ReportingPlatformFacade` must delegate to the focused Facades — it must
  not re-implement any logic itself.
- Callers that only need recipient management should be able to depend on
  `RecipientGroupFacade` alone, without importing anything related to reports
  or scheduling.

---

## Subsystem classes provided

The exercise file contains all three subsystem groups:

**Report delivery** (same as Exercise 2):
`SalesDataFetcher`, `KpiFetcher`, `ReportFormatter`, `ReportArchiver`,
`ReportEmailer`

**Scheduling**:
`ReportScheduler` — `schedule(report_type, cron_expr, recipients) -> str`,
`cancel(schedule_id) -> None`, `status(schedule_id) -> dict`

**Recipient groups**:
`RecipientGroupStore` — `add(group_name, emails) -> None`,
`remove(group_name) -> None`, `list_all() -> dict`

---

## File to edit

`exercise3.py`

Run the tests with:

```bash
python -m pytest exercise3.py -v
```
