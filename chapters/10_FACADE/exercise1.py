"""
Facade Exercise 1: Basic Report Facade

Your task: implement ReportFacade.

Do not modify the subsystem classes below.
"""


# ---------------------------------------------------------------------------
# Subsystem classes — do not modify these
# ---------------------------------------------------------------------------

class SalesDataFetcher:
    """Fetches raw sales data from a data store."""

    def fetch_weekly_sales(self) -> dict:
        return {
            "week": "2024-W42",
            "total_revenue": 48_320.00,
            "total_orders": 214,
            "top_product": "Widget Pro",
        }


class ReportFormatter:
    """Formats raw data into a human-readable report string."""

    def format(self, data: dict) -> str:
        return (
            f"Weekly Sales Report — {data['week']}\n"
            f"Revenue : ${data['total_revenue']:,.2f}\n"
            f"Orders  : {data['total_orders']}\n"
            f"Top item: {data['top_product']}"
        )


class ReportEmailer:
    """Sends a report string to a list of email addresses."""

    def __init__(self):
        self.sent: list[dict] = []   # records calls for test inspection

    def send(self, report: str, recipients: list[str]) -> None:
        for recipient in recipients:
            self.sent.append({"to": recipient, "body": report})


# ---------------------------------------------------------------------------
# Your code goes here
# ---------------------------------------------------------------------------

class ReportFacade:
    def __init__(self, data_fetcher, formatter, emailer):
        # TODO: store the subsystem objects
        pass

    def send_weekly_report(self, recipients: list[str]) -> None:
        # TODO: orchestrate the three subsystem calls
        pass


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_send_weekly_report_calls_all_subsystems():
    emailer = ReportEmailer()
    facade = ReportFacade(
        data_fetcher=SalesDataFetcher(),
        formatter=ReportFormatter(),
        emailer=emailer,
    )

    facade.send_weekly_report(recipients=["alice@example.com"])

    assert len(emailer.sent) == 1


def test_send_weekly_report_delivers_to_all_recipients():
    emailer = ReportEmailer()
    facade = ReportFacade(
        data_fetcher=SalesDataFetcher(),
        formatter=ReportFormatter(),
        emailer=emailer,
    )

    facade.send_weekly_report(
        recipients=["alice@example.com", "bob@example.com", "carol@example.com"]
    )

    assert len(emailer.sent) == 3
    recipients_sent_to = [m["to"] for m in emailer.sent]
    assert "alice@example.com" in recipients_sent_to
    assert "bob@example.com" in recipients_sent_to
    assert "carol@example.com" in recipients_sent_to


def test_send_weekly_report_email_body_contains_revenue():
    emailer = ReportEmailer()
    facade = ReportFacade(
        data_fetcher=SalesDataFetcher(),
        formatter=ReportFormatter(),
        emailer=emailer,
    )

    facade.send_weekly_report(recipients=["alice@example.com"])

    body = emailer.sent[0]["body"]
    assert "48,320.00" in body


def test_caller_only_needs_the_facade():
    """
    The caller should only depend on ReportFacade, not on the subsystem classes.
    This test verifies the Facade can be replaced with a fake in tests.
    """

    class FakeReportFacade:
        def __init__(self):
            self.calls = []

        def send_weekly_report(self, recipients):
            self.calls.append(recipients)

    fake = FakeReportFacade()
    fake.send_weekly_report(["alice@example.com"])

    assert len(fake.calls) == 1
