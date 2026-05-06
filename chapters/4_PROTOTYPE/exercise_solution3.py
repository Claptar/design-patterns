from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import unittest


@dataclass
class DataSource:
    name: str
    connection_string: str


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
    data_source: DataSource
    widgets: list[Widget] = field(default_factory=list)
    filters: dict[str, str] = field(default_factory=dict)
    refresh_minutes: int = 60
    cache: dict[str, object] = field(default_factory=dict)

    def clone(self, **changes) -> "Dashboard":
        cloned = Dashboard(
            title=self.title,
            owner=self.owner,
            layout=self.layout,
            data_source=self.data_source,
            widgets=deepcopy(self.widgets),
            filters=deepcopy(self.filters),
            refresh_minutes=self.refresh_minutes,
            cache={},
        )

        for field_name, value in changes.items():
            if not hasattr(cloned, field_name):
                raise AttributeError(f"Dashboard has no field: {field_name}")
            setattr(cloned, field_name, value)

        return cloned


class DashboardCustomCloneTests(unittest.TestCase):
    def make_dashboard(self) -> Dashboard:
        source = DataSource(
            name="warehouse",
            connection_string="postgresql://analytics-db",
        )
        dashboard = Dashboard(
            title="Sales Dashboard Template",
            owner="analytics-team",
            layout="two-column",
            data_source=source,
            widgets=[
                Widget("Revenue", "revenue", "line"),
                Widget("New Customers", "new_customers", "bar"),
            ],
            filters={"region": "all", "segment": "all"},
            refresh_minutes=30,
        )
        dashboard.cache["last_result"] = {"revenue": 1000}
        return dashboard

    def test_clone_applies_changes(self):
        template = self.make_dashboard()

        cloned = template.clone(title="UK Sales Dashboard", owner="Alice")

        self.assertIsNot(cloned, template)
        self.assertEqual(cloned.title, "UK Sales Dashboard")
        self.assertEqual(cloned.owner, "Alice")
        self.assertEqual(cloned.layout, "two-column")

    def test_widgets_and_filters_are_independent(self):
        template = self.make_dashboard()
        cloned = template.clone(title="UK Sales Dashboard")

        cloned.filters["region"] = "UK"
        cloned.widgets[0].title = "UK Revenue"

        self.assertEqual(template.filters["region"], "all")
        self.assertEqual(template.widgets[0].title, "Revenue")
        self.assertIsNot(cloned.filters, template.filters)
        self.assertIsNot(cloned.widgets, template.widgets)
        self.assertIsNot(cloned.widgets[0], template.widgets[0])

    def test_data_source_is_shared(self):
        template = self.make_dashboard()
        cloned = template.clone(title="UK Sales Dashboard")

        self.assertIs(cloned.data_source, template.data_source)

    def test_cache_is_reset(self):
        template = self.make_dashboard()
        cloned = template.clone(title="UK Sales Dashboard")

        self.assertEqual(template.cache, {"last_result": {"revenue": 1000}})
        self.assertEqual(cloned.cache, {})
        self.assertIsNot(cloned.cache, template.cache)

    def test_unknown_change_raises_attribute_error(self):
        template = self.make_dashboard()

        with self.assertRaises(AttributeError):
            template.clone(unknown_field="value")


if __name__ == "__main__":
    unittest.main()
