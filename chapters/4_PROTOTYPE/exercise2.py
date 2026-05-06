from __future__ import annotations

from copy import deepcopy
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
        """Return an independent copied dashboard with the requested changes."""
        # TODO:
        # 1. Deep-copy the current dashboard.
        # 2. Apply all keyword changes to the copy.
        # 3. Return the copy.
        raise NotImplementedError


class DashboardDeepCloneTests(unittest.TestCase):
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

    def test_clone_can_change_top_level_fields(self):
        template = self.make_dashboard()

        cloned = template.clone(title="UK Sales Dashboard", owner="Alice")

        self.assertIsNot(cloned, template)
        self.assertEqual(cloned.title, "UK Sales Dashboard")
        self.assertEqual(cloned.owner, "Alice")
        self.assertEqual(template.title, "Sales Dashboard Template")
        self.assertEqual(template.owner, "analytics-team")

    def test_filters_are_independent(self):
        template = self.make_dashboard()
        cloned = template.clone(title="UK Sales Dashboard")

        cloned.filters["region"] = "UK"

        self.assertEqual(cloned.filters["region"], "UK")
        self.assertEqual(template.filters["region"], "all")
        self.assertIsNot(cloned.filters, template.filters)

    def test_widgets_are_independent(self):
        template = self.make_dashboard()
        cloned = template.clone(title="UK Sales Dashboard")

        cloned.widgets[0].title = "UK Revenue"
        cloned.widgets.append(Widget("UK Churn", "churn", "line"))

        self.assertEqual(cloned.widgets[0].title, "UK Revenue")
        self.assertEqual(template.widgets[0].title, "Revenue")
        self.assertEqual(len(cloned.widgets), 3)
        self.assertEqual(len(template.widgets), 2)
        self.assertIsNot(cloned.widgets, template.widgets)
        self.assertIsNot(cloned.widgets[0], template.widgets[0])


if __name__ == "__main__":
    unittest.main()
