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


class DashboardFactory:
    analytics_source = DataSource(
        name="warehouse",
        connection_string="postgresql://analytics-db",
    )

    sales_dashboard = Dashboard(
        title="Sales Dashboard Template",
        owner="analytics-team",
        layout="two-column",
        data_source=analytics_source,
        widgets=[
            Widget("Revenue", "revenue", "line"),
            Widget("New Customers", "new_customers", "bar"),
        ],
        filters={"region": "all", "segment": "all"},
        refresh_minutes=30,
    )

    marketing_dashboard = Dashboard(
        title="Marketing Dashboard Template",
        owner="marketing-ops",
        layout="single-column",
        data_source=analytics_source,
        widgets=[
            Widget("Leads", "leads", "bar"),
            Widget("Conversion Rate", "conversion_rate", "line"),
        ],
        filters={"region": "all", "channel": "all"},
        refresh_minutes=60,
    )

    @classmethod
    def _new_dashboard(cls, prototype: Dashboard, title: str, owner: str, region: str) -> Dashboard:
        dashboard = prototype.clone(title=title, owner=owner)
        dashboard.filters["region"] = region
        return dashboard

    @classmethod
    def new_sales_dashboard(cls, title: str, owner: str, region: str) -> Dashboard:
        return cls._new_dashboard(cls.sales_dashboard, title, owner, region)

    @classmethod
    def new_marketing_dashboard(cls, title: str, owner: str, region: str) -> Dashboard:
        return cls._new_dashboard(cls.marketing_dashboard, title, owner, region)


class DashboardPrototypeFactoryTests(unittest.TestCase):
    def test_new_sales_dashboard_uses_sales_prototype(self):
        dashboard = DashboardFactory.new_sales_dashboard("UK Sales Dashboard", "Alice", "UK")
        self.assertEqual(dashboard.title, "UK Sales Dashboard")
        self.assertEqual(dashboard.owner, "Alice")
        self.assertEqual(dashboard.filters["region"], "UK")
        self.assertEqual(dashboard.layout, "two-column")
        self.assertEqual([widget.metric for widget in dashboard.widgets], ["revenue", "new_customers"])

    def test_new_marketing_dashboard_uses_marketing_prototype(self):
        dashboard = DashboardFactory.new_marketing_dashboard(
            "Germany Marketing Dashboard", "Bruno", "Germany"
        )
        self.assertEqual(dashboard.title, "Germany Marketing Dashboard")
        self.assertEqual(dashboard.owner, "Bruno")
        self.assertEqual(dashboard.filters["region"], "Germany")
        self.assertEqual(dashboard.layout, "single-column")
        self.assertEqual([widget.metric for widget in dashboard.widgets], ["leads", "conversion_rate"])

    def test_created_dashboards_are_independent(self):
        uk = DashboardFactory.new_sales_dashboard("UK Sales", "Alice", "UK")
        de = DashboardFactory.new_sales_dashboard("Germany Sales", "Bruno", "Germany")
        uk.filters["segment"] = "enterprise"
        uk.widgets[0].title = "UK Revenue"
        self.assertEqual(de.filters["segment"], "all")
        self.assertEqual(de.widgets[0].title, "Revenue")
        self.assertIsNot(uk.filters, de.filters)
        self.assertIsNot(uk.widgets, de.widgets)
        self.assertIsNot(uk.widgets[0], de.widgets[0])

    def test_prototypes_are_not_mutated(self):
        dashboard = DashboardFactory.new_sales_dashboard("UK Sales", "Alice", "UK")
        dashboard.widgets[0].title = "UK Revenue"
        dashboard.filters["region"] = "UK"
        prototype = DashboardFactory.sales_dashboard
        self.assertEqual(prototype.title, "Sales Dashboard Template")
        self.assertEqual(prototype.owner, "analytics-team")
        self.assertEqual(prototype.widgets[0].title, "Revenue")
        self.assertEqual(prototype.filters["region"], "all")

    def test_data_source_is_shared_with_prototype(self):
        dashboard = DashboardFactory.new_sales_dashboard("UK Sales", "Alice", "UK")
        self.assertIs(dashboard.data_source, DashboardFactory.sales_dashboard.data_source)


DISCUSSION = """
Explanation
-----------
This part combines Factory and Prototype.

The factory owns the named prototypes:

    sales_dashboard
    marketing_dashboard

The public methods give clear creation paths:

    new_sales_dashboard(...)
    new_marketing_dashboard(...)

The private helper contains the common clone-and-customize logic:

    clone prototype
    set title
    set owner
    set region filter

This keeps callers away from construction details.

Why this is a prototype factory
-------------------------------
A normal factory often maps a key or method to a class constructor.

A prototype factory maps a key or method to a preconfigured object, then clones
that object.

Mental model:

    normal factory:     choose class -> construct
    prototype factory:  choose prototype -> clone -> customize

Pitfalls
--------
The prototypes are class-level mutable objects. That is acceptable for a small
exercise, but in production you should treat them as read-only templates.

Do not mutate this directly:

    DashboardFactory.sales_dashboard.filters["region"] = "UK"

That would change future clones. If that is a concern, hide prototypes more
strictly or use immutable value objects where possible.
"""


if __name__ == "__main__":
    unittest.main()
