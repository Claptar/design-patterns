"""
Facade Exercise 3: Avoiding the God Object

Your task:
  1. Implement ReportFacade (delivery only)
  2. Implement SchedulingFacade
  3. Implement RecipientGroupFacade
  4. Implement ReportingPlatformFacade that composes the three

Do not modify the subsystem classes below.
"""


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ArchiveError(Exception):
    pass


class ReportDeliveryError(Exception):
    pass


# ---------------------------------------------------------------------------
# Subsystem classes — do not modify these
# ---------------------------------------------------------------------------

# --- Report delivery ---

class SalesDataFetcher:
    def fetch_weekly_sales(self) -> dict:
        return {
            "week": "2024-W42",
            "total_revenue": 48_320.00,
            "total_orders": 214,
            "top_product": "Widget Pro",
        }

    def fetch_monthly_sales(self) -> dict:
        return {
            "month": "2024-10",
            "total_revenue": 198_740.00,
            "total_orders": 891,
            "top_product": "Widget Pro",
        }


class KpiFetcher:
    def fetch_kpis(self) -> dict:
        return {
            "customer_satisfaction": 4.7,
            "churn_rate": 0.023,
            "new_customers": 142,
        }


class ReportFormatter:
    def format(self, data: dict) -> str:
        return (
            f"Weekly Sales Report — {data['week']}\n"
            f"Revenue : ${data['total_revenue']:,.2f}\n"
            f"Orders  : {data['total_orders']}"
        )

    def format_executive(self, data: dict, kpis: dict) -> str:
        return (
            f"Executive Summary — {data['month']}\n"
            f"Revenue     : ${data['total_revenue']:,.2f}\n"
            f"Satisfaction: {kpis['customer_satisfaction']}/5.0"
        )


class ReportArchiver:
    def __init__(self, should_fail: bool = False):
        self.saved: list[dict] = []
        self._should_fail = should_fail

    def save(self, report: str, filename: str) -> None:
        if self._should_fail:
            raise ArchiveError("Disk full")
        self.saved.append({"filename": filename, "content": report})


class ReportEmailer:
    def __init__(self):
        self.sent: list[dict] = []

    def send(self, report: str, recipients: list[str]) -> None:
        for recipient in recipients:
            self.sent.append({"to": recipient, "body": report})


# --- Scheduling ---

class ReportScheduler:
    def __init__(self):
        self._schedules: dict[str, dict] = {}
        self._next_id = 1

    def schedule(self, report_type: str, cron_expr: str, recipients: list[str]) -> str:
        schedule_id = f"sched_{self._next_id}"
        self._next_id += 1
        self._schedules[schedule_id] = {
            "report_type": report_type,
            "cron": cron_expr,
            "recipients": recipients,
            "active": True,
        }
        return schedule_id

    def cancel(self, schedule_id: str) -> None:
        if schedule_id in self._schedules:
            self._schedules[schedule_id]["active"] = False

    def status(self, schedule_id: str) -> dict:
        return self._schedules.get(schedule_id, {})


# --- Recipient groups ---

class RecipientGroupStore:
    def __init__(self):
        self._groups: dict[str, list[str]] = {}

    def add(self, group_name: str, emails: list[str]) -> None:
        self._groups[group_name] = emails

    def remove(self, group_name: str) -> None:
        self._groups.pop(group_name, None)

    def list_all(self) -> dict:
        return dict(self._groups)


# ---------------------------------------------------------------------------
# Your code goes here
# ---------------------------------------------------------------------------

class ReportFacade:
    """Handles report delivery only."""

    def __init__(
        self,
        data_fetcher,
        formatter,
        emailer,
        kpi_fetcher=None,
        archiver=None,
    ):
        # TODO
        pass

    def send_weekly_report(self, recipients: list[str]) -> None:
        # TODO
        pass

    def send_monthly_executive_summary(
        self,
        recipients: list[str],
        archive_filename: str,
    ) -> None:
        # TODO
        pass


class SchedulingFacade:
    """Handles report scheduling only."""

    def __init__(self, scheduler):
        # TODO
        pass

    def schedule_report(
        self,
        report_type: str,
        cron_expr: str,
        recipients: list[str],
    ) -> str:
        # TODO
        pass

    def cancel_scheduled_report(self, schedule_id: str) -> None:
        # TODO
        pass

    def get_schedule_status(self, schedule_id: str) -> dict:
        # TODO
        pass


class RecipientGroupFacade:
    """Handles recipient group management only."""

    def __init__(self, group_store):
        # TODO
        pass

    def add_recipient_group(self, group_name: str, emails: list[str]) -> None:
        # TODO
        pass

    def remove_recipient_group(self, group_name: str) -> None:
        # TODO
        pass

    def list_recipient_groups(self) -> dict:
        # TODO
        pass


class ReportingPlatformFacade:
    """
    Composes all three focused Facades for callers that need the full platform.
    Must not re-implement any logic — only delegate.
    """

    def __init__(
        self,
        report_facade: ReportFacade,
        scheduling_facade: SchedulingFacade,
        recipient_facade: RecipientGroupFacade,
    ):
        # TODO
        pass

    def send_weekly_report(self, recipients: list[str]) -> None:
        # TODO
        pass

    def send_monthly_executive_summary(
        self, recipients: list[str], archive_filename: str
    ) -> None:
        # TODO
        pass

    def schedule_report(
        self, report_type: str, cron_expr: str, recipients: list[str]
    ) -> str:
        # TODO
        pass

    def cancel_scheduled_report(self, schedule_id: str) -> None:
        # TODO
        pass

    def get_schedule_status(self, schedule_id: str) -> dict:
        # TODO
        pass

    def add_recipient_group(self, group_name: str, emails: list[str]) -> None:
        # TODO
        pass

    def remove_recipient_group(self, group_name: str) -> None:
        # TODO
        pass

    def list_recipient_groups(self) -> dict:
        # TODO
        pass


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

# --- ReportFacade ---

def test_report_facade_sends_weekly():
    emailer = ReportEmailer()
    facade = ReportFacade(
        data_fetcher=SalesDataFetcher(),
        formatter=ReportFormatter(),
        emailer=emailer,
    )
    facade.send_weekly_report(["alice@example.com"])
    assert len(emailer.sent) == 1


def test_report_facade_sends_monthly():
    emailer = ReportEmailer()
    facade = ReportFacade(
        data_fetcher=SalesDataFetcher(),
        formatter=ReportFormatter(),
        emailer=emailer,
        kpi_fetcher=KpiFetcher(),
        archiver=ReportArchiver(),
    )
    facade.send_monthly_executive_summary(
        recipients=["board@example.com"],
        archive_filename="exec.txt",
    )
    assert len(emailer.sent) == 1


# --- SchedulingFacade ---

def test_scheduling_facade_creates_schedule():
    scheduler = ReportScheduler()
    facade = SchedulingFacade(scheduler=scheduler)

    schedule_id = facade.schedule_report(
        report_type="weekly",
        cron_expr="0 8 * * MON",
        recipients=["team@example.com"],
    )

    assert schedule_id is not None
    assert schedule_id != ""


def test_scheduling_facade_cancel_deactivates_schedule():
    scheduler = ReportScheduler()
    facade = SchedulingFacade(scheduler=scheduler)

    schedule_id = facade.schedule_report("weekly", "0 8 * * MON", ["team@example.com"])
    facade.cancel_scheduled_report(schedule_id)

    status = facade.get_schedule_status(schedule_id)
    assert status["active"] is False


def test_scheduling_facade_status_returns_schedule_info():
    scheduler = ReportScheduler()
    facade = SchedulingFacade(scheduler=scheduler)

    schedule_id = facade.schedule_report("monthly", "0 9 1 * *", ["board@example.com"])
    status = facade.get_schedule_status(schedule_id)

    assert status["report_type"] == "monthly"
    assert status["cron"] == "0 9 1 * *"


# --- RecipientGroupFacade ---

def test_recipient_facade_adds_group():
    store = RecipientGroupStore()
    facade = RecipientGroupFacade(group_store=store)

    facade.add_recipient_group("board", ["ceo@example.com", "cfo@example.com"])
    groups = facade.list_recipient_groups()

    assert "board" in groups
    assert "ceo@example.com" in groups["board"]


def test_recipient_facade_removes_group():
    store = RecipientGroupStore()
    facade = RecipientGroupFacade(group_store=store)

    facade.add_recipient_group("board", ["ceo@example.com"])
    facade.remove_recipient_group("board")
    groups = facade.list_recipient_groups()

    assert "board" not in groups


# --- ReportingPlatformFacade ---

def test_platform_facade_delegates_weekly_report():
    emailer = ReportEmailer()
    platform = ReportingPlatformFacade(
        report_facade=ReportFacade(
            data_fetcher=SalesDataFetcher(),
            formatter=ReportFormatter(),
            emailer=emailer,
        ),
        scheduling_facade=SchedulingFacade(ReportScheduler()),
        recipient_facade=RecipientGroupFacade(RecipientGroupStore()),
    )

    platform.send_weekly_report(["alice@example.com"])

    assert len(emailer.sent) == 1


def test_platform_facade_delegates_scheduling():
    scheduler = ReportScheduler()
    platform = ReportingPlatformFacade(
        report_facade=ReportFacade(
            data_fetcher=SalesDataFetcher(),
            formatter=ReportFormatter(),
            emailer=ReportEmailer(),
        ),
        scheduling_facade=SchedulingFacade(scheduler),
        recipient_facade=RecipientGroupFacade(RecipientGroupStore()),
    )

    schedule_id = platform.schedule_report(
        "weekly", "0 8 * * MON", ["team@example.com"]
    )

    assert schedule_id is not None
    status = platform.get_schedule_status(schedule_id)
    assert status["active"] is True


def test_platform_facade_delegates_recipient_management():
    store = RecipientGroupStore()
    platform = ReportingPlatformFacade(
        report_facade=ReportFacade(
            data_fetcher=SalesDataFetcher(),
            formatter=ReportFormatter(),
            emailer=ReportEmailer(),
        ),
        scheduling_facade=SchedulingFacade(ReportScheduler()),
        recipient_facade=RecipientGroupFacade(store),
    )

    platform.add_recipient_group("board", ["ceo@example.com"])
    groups = platform.list_recipient_groups()

    assert "board" in groups


def test_recipient_facade_usable_without_report_dependencies():
    """
    RecipientGroupFacade should work with no knowledge of reports or scheduling.
    This test instantiates it alone — no SalesDataFetcher, no scheduler.
    """
    store = RecipientGroupStore()
    facade = RecipientGroupFacade(group_store=store)

    facade.add_recipient_group("sales", ["sales@example.com"])
    groups = facade.list_recipient_groups()

    assert "sales" in groups
