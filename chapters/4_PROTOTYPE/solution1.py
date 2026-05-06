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
        cloned = template.clone(title="UK Sales Dashboard", owner="Alice")
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


DISCUSSION = """
Explanation
-----------
This is the smallest form of the Prototype pattern.

The existing Dashboard object acts as the prototype. The clone() method creates a new
Dashboard object by copying the current one, then applies only the requested changes.

Why this is useful
------------------
The caller does not need to rebuild the whole dashboard from scratch. It can say:

    uk_dashboard = template.clone(title="UK Sales Dashboard", owner="Alice")

That reads as: "Start from the template, but change these fields."

Pitfall
-------
This solution uses copy.copy(), which is a shallow copy. That is enough for the
first exercise because the tests only check top-level fields.

But the Dashboard contains nested mutable objects: widgets and filters. In the next
exercise, shallow copying will become a problem because the original and clone can
accidentally share those nested objects.
"""


if __name__ == "__main__":
    unittest.main()
