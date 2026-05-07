"""
Facade Exercise 1: Solution
"""


# ---------------------------------------------------------------------------
# Subsystem classes — unchanged
# ---------------------------------------------------------------------------

class SalesDataFetcher:
    def fetch_weekly_sales(self) -> dict:
        return {
            "week": "2024-W42",
            "total_revenue": 48_320.00,
            "total_orders": 214,
            "top_product": "Widget Pro",
        }


class ReportFormatter:
    def format(self, data: dict) -> str:
        return (
            f"Weekly Sales Report — {data['week']}\n"
            f"Revenue : ${data['total_revenue']:,.2f}\n"
            f"Orders  : {data['total_orders']}\n"
            f"Top item: {data['top_product']}"
        )


class ReportEmailer:
    def __init__(self):
        self.sent: list[dict] = []

    def send(self, report: str, recipients: list[str]) -> None:
        for recipient in recipients:
            self.sent.append({"to": recipient, "body": report})


# ---------------------------------------------------------------------------
# Solution
# ---------------------------------------------------------------------------

class ReportFacade:
    def __init__(self, data_fetcher, formatter, emailer):
        self._data_fetcher = data_fetcher
        self._formatter = formatter
        self._emailer = emailer

    def send_weekly_report(self, recipients: list[str]) -> None:
        data = self._data_fetcher.fetch_weekly_sales()
        report = self._formatter.format(data)
        self._emailer.send(report, recipients)


# ---------------------------------------------------------------------------
# Tests (same as exercise1.py)
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
    class FakeReportFacade:
        def __init__(self):
            self.calls = []

        def send_weekly_report(self, recipients):
            self.calls.append(recipients)

    fake = FakeReportFacade()
    fake.send_weekly_report(["alice@example.com"])

    assert len(fake.calls) == 1
