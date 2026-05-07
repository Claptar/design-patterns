"""
Facade Exercise 2: Solution
"""


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ArchiveError(Exception):
    pass


class ReportDeliveryError(Exception):
    pass


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
            f"Orders  : {data['total_orders']}\n"
            f"Top item: {data['top_product']}"
        )

    def format_executive(self, data: dict, kpis: dict) -> str:
        return (
            f"Executive Summary — {data['month']}\n"
            f"Revenue     : ${data['total_revenue']:,.2f}\n"
            f"Orders      : {data['total_orders']}\n"
            f"Satisfaction: {kpis['customer_satisfaction']}/5.0\n"
            f"Churn rate  : {kpis['churn_rate']:.1%}\n"
            f"New customers: {kpis['new_customers']}"
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


# ---------------------------------------------------------------------------
# Solution
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Tests (same as exercise2.py)
# ---------------------------------------------------------------------------

def test_weekly_report_still_works():
    emailer = ReportEmailer()
    facade = ReportFacade(
        data_fetcher=SalesDataFetcher(),
        formatter=ReportFormatter(),
        emailer=emailer,
    )
    facade.send_weekly_report(recipients=["alice@example.com"])
    assert len(emailer.sent) == 1


def test_monthly_summary_archives_before_emailing():
    emailer = ReportEmailer()
    archiver = ReportArchiver()
    facade = ReportFacade(
        data_fetcher=SalesDataFetcher(),
        formatter=ReportFormatter(),
        emailer=emailer,
        kpi_fetcher=KpiFetcher(),
        archiver=archiver,
    )

    facade.send_monthly_executive_summary(
        recipients=["board@example.com"],
        archive_filename="exec_2024_10.txt",
    )

    assert len(archiver.saved) == 1
    assert archiver.saved[0]["filename"] == "exec_2024_10.txt"


def test_monthly_summary_sends_email():
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
        archive_filename="exec_2024_10.txt",
    )

    assert len(emailer.sent) == 1
    assert "board@example.com" == emailer.sent[0]["to"]


def test_monthly_summary_email_contains_kpi_data():
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
        archive_filename="exec_2024_10.txt",
    )

    body = emailer.sent[0]["body"]
    assert "4.7" in body
    assert "142" in body


def test_archive_failure_raises_report_delivery_error():
    emailer = ReportEmailer()
    archiver = ReportArchiver(should_fail=True)
    facade = ReportFacade(
        data_fetcher=SalesDataFetcher(),
        formatter=ReportFormatter(),
        emailer=emailer,
        kpi_fetcher=KpiFetcher(),
        archiver=archiver,
    )

    try:
        facade.send_monthly_executive_summary(
            recipients=["board@example.com"],
            archive_filename="exec_2024_10.txt",
        )
        assert False, "Expected ReportDeliveryError"
    except ReportDeliveryError:
        pass
    except ArchiveError:
        assert False, "ArchiveError must not escape the Facade"


def test_email_not_sent_when_archiving_fails():
    emailer = ReportEmailer()
    archiver = ReportArchiver(should_fail=True)
    facade = ReportFacade(
        data_fetcher=SalesDataFetcher(),
        formatter=ReportFormatter(),
        emailer=emailer,
        kpi_fetcher=KpiFetcher(),
        archiver=archiver,
    )

    try:
        facade.send_monthly_executive_summary(
            recipients=["board@example.com"],
            archive_filename="exec_2024_10.txt",
        )
    except ReportDeliveryError:
        pass

    assert len(emailer.sent) == 0, "Email must not be sent when archiving fails"
