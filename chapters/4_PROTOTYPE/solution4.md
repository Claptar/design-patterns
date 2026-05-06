---
layout: default
title: Solution 4 - Dashboard Prototype Factory
---

# Solution 4: Dashboard Prototype Factory

## Completed idea

`DashboardFactory` stores two preconfigured prototype dashboards.

Factory methods clone the right prototype, apply caller-provided customizations, and return the result.

---

## Solution

```python
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
```

---

## The structure

```text
DashboardFactory
├── sales_dashboard prototype
├── marketing_dashboard prototype
│
├── new_sales_dashboard(...)
│   └── clone sales prototype, set title, owner, region
│
└── new_marketing_dashboard(...)
    └── clone marketing prototype, set title, owner, region
```

The `_new_dashboard` private method handles the shared cloning logic.

Each public method picks the right prototype and delegates.

---

## Why the prototypes are not mutated

The `clone()` method from exercise 3 uses `deepcopy()` for `widgets` and `filters`.

So each created dashboard owns its own copies of those collections.

Mutating a created dashboard's widgets or filters does not reach back into the factory's prototype.

---

[Back to exercise](exercise4.md) · [Solution script](exercise_solution4.py)
