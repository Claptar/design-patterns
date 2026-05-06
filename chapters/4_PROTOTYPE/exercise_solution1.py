from __future__ import annotations

from copy import copy
from dataclasses import dataclass, field
import unittest


@dataclass
class Widget:
    title: str
    metric: str
    chart_type: str


@dataclass
class Dashboard:
    title: str
    owner: str
    layout: str
    widgets: list[Widget] = field(default_factory=list)
    filters: dict[str, str] = field(default_factory=dict)
    refresh_minutes: int = 60

    def clone(self, **changes) -> "Dashboard":
        cloned = copy(self)

        for field_name, value in changes.items():
            setattr(cloned, field_name, value)

        return cloned


class DashboardCloneTests(unittest.TestCase):
    def make_dashboard(self) -> Dashboard:
        return Dashboard(
            title="Sales Dashboard Template",
            owner="analytics-team",
            layout="two-column",
            widgets=[
                Widget("Revenue", "revenue", "line"),
                Widget("New Customers", "new_customers", "bar"),
            ],
            filters={"region": "all", "segment": "all"},
            refresh_minutes=30,
        )

    def test_clone_returns_new_dashboard_object(self):
        template = self.make_dashboard()

        cloned = template.clone()

        self.assertIsNot(cloned, template)
        self.assertIsInstance(cloned, Dashboard)

    def test_clone_can_change_top_level_fields(self):
        template = self.make_dashboard()

        cloned = template.clone(
            title="UK Sales Dashboard",
            owner="Alice",
        )

        self.assertEqual(cloned.title, "UK Sales Dashboard")
        self.assertEqual(cloned.owner, "Alice")
        self.assertEqual(cloned.layout, "two-column")
        self.assertEqual(cloned.refresh_minutes, 30)

    def test_original_top_level_fields_are_not_changed(self):
        template = self.make_dashboard()

        cloned = template.clone(title="UK Sales Dashboard", owner="Alice")

        self.assertEqual(template.title, "Sales Dashboard Template")
        self.assertEqual(template.owner, "analytics-team")
        self.assertEqual(cloned.title, "UK Sales Dashboard")
        self.assertEqual(cloned.owner, "Alice")


if __name__ == "__main__":
    unittest.main()
