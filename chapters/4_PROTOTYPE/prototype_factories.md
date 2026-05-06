---
layout: default
title: Prototype Factories
---

# Prototype Factories

## 1. What problem are we trying to solve?

Sometimes a factory does not need to create objects from scratch.

Imagine a company dashboard system.

The product team uses dashboards like these:

```text
Executive dashboard
Sales dashboard
Support dashboard
Operations dashboard
```

Each dashboard has many settings:

```text
title
theme
layout
charts
filters
refresh interval
export format
permissions
```

A lot of those settings are repeated.

For example, every executive dashboard may use:

```text
executive theme
PDF export
monthly date filter
high-level KPI cards
revenue chart
customer growth chart
```

Every support dashboard may use:

```text
support theme
daily date filter
ticket volume chart
response time chart
SLA chart
```

Now suppose we need dashboards for different teams:

```text
Executive dashboard for UK
Executive dashboard for Germany
Support dashboard for Enterprise customers
Support dashboard for Trial customers
```

Without a prototype factory, the caller may have to repeat a lot of setup:

```python
uk_dashboard = Dashboard(
    title="Executive Dashboard - UK",
    theme="executive",
    layout="two-column",
    charts=[
        Chart("Revenue", "revenue"),
        Chart("Customer Growth", "customer_growth"),
    ],
    filters={"region": "UK", "period": "monthly"},
    refresh_minutes=60,
    export_format="pdf",
)

germany_dashboard = Dashboard(
    title="Executive Dashboard - Germany",
    theme="executive",
    layout="two-column",
    charts=[
        Chart("Revenue", "revenue"),
        Chart("Customer Growth", "customer_growth"),
    ],
    filters={"region": "Germany", "period": "monthly"},
    refresh_minutes=60,
    export_format="pdf",
)
```

The problem is not just that the code is long.

The deeper problem is:

> We already have a standard dashboard shape. Why rebuild that standard shape again and again?

That is the problem a **prototype factory** solves.

---

## 2. Concept introduction

A **prototype factory** is a factory that creates new objects by cloning preconfigured prototype objects.

It combines two creational ideas:

```text
Factory   -> choose which kind of object to create
Prototype -> create the object by copying an existing object
```

The factory does not say:

```text
Start from an empty object and configure every field manually.
```

Instead, it says:

```text
Start from this ready-made prototype.
Deep-copy it.
Customize the few fields that are different.
Return the copy.
```

The basic flow is:

```text
DashboardPrototypeFactory
    has executive_dashboard prototype
    has support_dashboard prototype

new_executive_dashboard(...)
    deep-copies executive_dashboard
    changes title and filters
    returns the new dashboard
```

In one sentence:

> A prototype factory is useful when the factory has a few standard template objects, and new objects should be customized copies of those templates.

---

## 3. The API we want

Before looking at implementation, start with the code we want to write.

We want this:

```python
uk_dashboard = DashboardFactory.new_executive_dashboard(
    title="Executive Dashboard - UK",
    region="UK",
)

enterprise_support_dashboard = DashboardFactory.new_support_dashboard(
    title="Support Dashboard - Enterprise",
    segment="enterprise",
)
```

This should read as:

```text
Give me a standard executive dashboard, customized for the UK.
Give me a standard support dashboard, customized for Enterprise customers.
```

The caller should not need to know:

```text
which charts belong on an executive dashboard
which theme to use
which layout to use
which export format to use
whether a deep copy is needed
which nested objects must be copied
```

The factory should own that construction knowledge.

---

## 4. Final objects

First, define the objects we want to create.

```python
from dataclasses import dataclass, field


@dataclass
class Chart:
    title: str
    metric: str


@dataclass
class Dashboard:
    title: str
    theme: str
    layout: str
    charts: list[Chart] = field(default_factory=list)
    filters: dict[str, str] = field(default_factory=dict)
    refresh_minutes: int = 60
    export_format: str = "pdf"

    def __str__(self):
        chart_titles = ", ".join(chart.title for chart in self.charts)
        return (
            f"{self.title} "
            f"[{self.theme}, {self.layout}] "
            f"charts=({chart_titles}) "
            f"filters={self.filters}"
        )
```

The `Dashboard` class represents a completed dashboard.

It does not need to know about all the standard dashboard templates. That is the factory's job.

---

## 5. Prototype factory implementation

Now we create a factory that stores prototype dashboards.

```python
import copy


class DashboardFactory:
    _executive_dashboard = Dashboard(
        title="",
        theme="executive",
        layout="two-column",
        charts=[
            Chart("Revenue", "revenue"),
            Chart("Customer Growth", "customer_growth"),
            Chart("Gross Margin", "gross_margin"),
        ],
        filters={"period": "monthly"},
        refresh_minutes=60,
        export_format="pdf",
    )

    _support_dashboard = Dashboard(
        title="",
        theme="support",
        layout="three-column",
        charts=[
            Chart("Ticket Volume", "ticket_volume"),
            Chart("Response Time", "response_time"),
            Chart("SLA Compliance", "sla_compliance"),
        ],
        filters={"period": "daily"},
        refresh_minutes=15,
        export_format="html",
    )

    @classmethod
    def _new_dashboard(cls, prototype: Dashboard, title: str, **filters) -> Dashboard:
        dashboard = copy.deepcopy(prototype)
        dashboard.title = title
        dashboard.filters.update(filters)
        return dashboard

    @classmethod
    def new_executive_dashboard(cls, title: str, region: str) -> Dashboard:
        return cls._new_dashboard(
            cls._executive_dashboard,
            title,
            region=region,
        )

    @classmethod
    def new_support_dashboard(cls, title: str, segment: str) -> Dashboard:
        return cls._new_dashboard(
            cls._support_dashboard,
            title,
            segment=segment,
        )
```

Usage:

```python
uk_dashboard = DashboardFactory.new_executive_dashboard(
    title="Executive Dashboard - UK",
    region="UK",
)

enterprise_support_dashboard = DashboardFactory.new_support_dashboard(
    title="Support Dashboard - Enterprise",
    segment="enterprise",
)

print(uk_dashboard)
print(enterprise_support_dashboard)
```

Possible output:

```text
Executive Dashboard - UK [executive, two-column] charts=(Revenue, Customer Growth, Gross Margin) filters={'period': 'monthly', 'region': 'UK'}
Support Dashboard - Enterprise [support, three-column] charts=(Ticket Volume, Response Time, SLA Compliance) filters={'period': 'daily', 'segment': 'enterprise'}
```

The important thing is that the caller gets a customized dashboard with one clear method call.

---

## 6. What makes this a prototype factory?

The prototypes are here:

```python
_executive_dashboard = Dashboard(...)
_support_dashboard = Dashboard(...)
```

They are not meant to be used directly by application code.

They are template objects.

The cloning happens here:

```python
dashboard = copy.deepcopy(prototype)
```

The customization happens here:

```python
dashboard.title = title
dashboard.filters.update(filters)
```

The public factory methods are here:

```python
new_executive_dashboard(...)
new_support_dashboard(...)
```

So the structure is:

```text
DashboardFactory
├── executive dashboard prototype
├── support dashboard prototype
│
├── new_executive_dashboard(...)
│   └── clone executive prototype and customize it
│
└── new_support_dashboard(...)
    └── clone support prototype and customize it
```

That is the pattern.

---

## 7. Why use `deepcopy`?

The dashboard contains nested mutable objects:

```text
Dashboard
├── charts: list[Chart]
└── filters: dict[str, str]
```

If we use a shallow copy, the new dashboards may accidentally share the same list or dictionary.

That would be dangerous.

For example, imagine this happened:

```python
uk_dashboard.charts.append(Chart("Net Revenue", "net_revenue"))
```

If the chart list were shared with the prototype, then future executive dashboards might unexpectedly include `Net Revenue` too.

That would be a prototype bug.

So the factory uses:

```python
copy.deepcopy(prototype)
```

This means:

```text
copy the Dashboard
copy its charts list
copy each Chart
copy its filters dictionary
```

Each created dashboard becomes independent from the prototype and from other created dashboards.

---

## 8. Natural example: report templates

Dashboards are one example. Report templates are another natural example.

A company may have standard report shapes:

```text
monthly sales report
weekly support report
quarterly finance report
customer health report
```

Each report has a standard structure:

```text
sections
charts
filters
export settings
layout
theme
```

When the company needs a new regional report, it usually does not want to design the whole report from zero.

It wants to say:

```text
Take the monthly sales report template.
Clone it.
Change the region to UK.
Change the title.
```

That is prototype factory thinking.

The caller asks for a known kind of report:

```python
report = ReportFactory.new_monthly_sales_report(
    title="Monthly Sales - UK",
    region="UK",
)
```

The factory hides the details:

```text
which sections belong in the report
which charts are included
which default filters are used
which export settings are standard
how to safely clone the template
```

This is natural because business templates are often copied and customized in real life.

---

## 9. Connection to earlier learned concepts

### Prototype factory versus Factory

A normal factory centralizes a creation decision.

It usually answers:

```text
Given this input, which concrete object should I create?
```

Example:

```python
importer = CustomerImporterFactory.create_for_file("customers.csv")
```

The factory may choose between:

```text
CsvCustomerImporter
JsonCustomerImporter
ExcelCustomerImporter
```

A prototype factory also centralizes a creation decision, but the decision is about which prototype to clone.

It answers:

```text
Given this request, which preconfigured object should I copy?
```

Example:

```python
dashboard = DashboardFactory.new_executive_dashboard(
    title="Executive Dashboard - UK",
    region="UK",
)
```

So:

```text
Factory:
    choose a class or constructor

Prototype factory:
    choose a prototype object and clone it
```

---

### Prototype factory versus Builder

Builder is useful when object creation is a step-by-step process.

For example:

```python
request = (
    HttpRequestBuilder()
    .post("/invoices")
    .with_json_body({"amount": 4900})
    .with_timeout(10)
    .build()
)
```

The builder is helpful because construction has rules and steps.

A prototype factory is different.

It is useful when the object already has a standard shape.

```python
dashboard = DashboardFactory.new_executive_dashboard(
    title="Executive Dashboard - UK",
    region="UK",
)
```

The prototype already knows the standard charts, layout, theme, and export format.

So:

```text
Builder:
    assemble this object step by step

Prototype factory:
    copy this standard object and customize a few values
```

---

### Prototype factory versus factory method as named constructor

A factory method as a named constructor usually belongs on the class being created.

Example:

```python
money = Money.from_dollars(12.99, "USD")
point = Point.from_polar(5, 0.927)
```

That is useful when one class has multiple clear ways to create itself.

A prototype factory is separate from the created class.

```python
dashboard = DashboardFactory.new_executive_dashboard(...)
```

That is useful when creation depends on a set of standard templates that should not live inside the final object class itself.

So:

```text
Factory method:
    this class knows how to create itself from a named input form

Prototype factory:
    this factory owns reusable template objects and clones them
```

---

## 10. Example from a popular Python package: scikit-learn

A useful data-science example is `sklearn.base.clone`.

In scikit-learn, `clone(estimator)` creates a new unfitted estimator with the same parameters as the original estimator. It deep-copies the estimator's model parameters but does not copy fitted data attached during training.

That is prototype-like.

```python
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier


logistic_prototype = LogisticRegression(max_iter=1000, C=0.5)
forest_prototype = RandomForestClassifier(n_estimators=200, random_state=42)

logistic_model = clone(logistic_prototype)
forest_model = clone(forest_prototype)
```

The prototypes are configured estimators:

```text
LogisticRegression(max_iter=1000, C=0.5)
RandomForestClassifier(n_estimators=200, random_state=42)
```

The clones are fresh estimators with the same constructor parameters.

A prototype factory around this idea could look like this:

```python
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier


class ModelFactory:
    _logistic_regression = LogisticRegression(max_iter=1000)
    _random_forest = RandomForestClassifier(n_estimators=200, random_state=42)

    @classmethod
    def _new_model(cls, prototype, **params):
        model = clone(prototype)
        model.set_params(**params)
        return model

    @classmethod
    def new_logistic_regression(cls, **params):
        return cls._new_model(cls._logistic_regression, **params)

    @classmethod
    def new_random_forest(cls, **params):
        return cls._new_model(cls._random_forest, **params)
```

Usage:

```python
small_logistic_model = ModelFactory.new_logistic_regression(C=0.25)
large_forest_model = ModelFactory.new_random_forest(n_estimators=500)
```

This is the same idea as the dashboard example:

```text
choose a configured prototype
clone it
apply small changes
return the fresh object
```

Reference: [scikit-learn `sklearn.base.clone` documentation](https://scikit-learn.org/stable/modules/generated/sklearn.base.clone.html).

---

## 11. When to use prototype factories

Use a prototype factory when object creation looks like this:

```text
Choose one of a few standard templates.
Copy it.
Change a few values.
Return the result.
```

Good situations:

| Situation | Why a prototype factory helps |
|---|---|
| Standard templates exist | The factory stores the templates as prototypes. |
| Objects have many repeated defaults | Defaults live in one prototype instead of many constructors. |
| Callers should use simple creation methods | `new_executive_dashboard(...)` is clearer than manual copying. |
| Nested objects need careful copying | The factory can consistently use `deepcopy` or custom cloning. |
| New objects are variations, not totally new shapes | A prototype captures the shared shape. |
| Construction details should be hidden | Callers do not need to know the internal object graph. |

Examples:

```text
dashboard templates
report templates
email campaign templates
game enemy templates
configured machine-learning estimators
workflow templates
document templates
```

---

## 12. When not to use prototype factories

Do not use a prototype factory when the constructor is already clear.

```python
point = Point(x=10, y=20)
```

This would add little value:

```python
point = PointFactory.new_point(10, 20)
```

Also avoid prototype factories when copying is dangerous.

Be careful with objects that contain:

```text
open files
database connections
network sockets
thread locks
live sessions
unique IDs
security tokens
large datasets
hidden mutable state
```

These objects often should not be blindly deep-copied.

For those cases, a custom factory or builder may be safer.

Also avoid prototype factories if the prototypes are likely to be mutated accidentally.

For example:

```python
DashboardFactory._executive_dashboard.charts.append(...)
```

That changes the template for future objects.

The practical rule is:

> Treat prototypes as read-only templates.

---

## 13. Practical rule of thumb

Ask:

> Am I creating a new object by starting from a standard example and changing a few details?

If yes, a prototype factory may help.

Ask:

> Are the repeated defaults more important than the construction steps?

If yes, a prototype factory may be better than a builder.

Ask:

> Is the main decision which concrete class to instantiate?

If yes, use a normal factory.

Ask:

> Is the main task to assemble a valid object through several steps?

If yes, use a builder.

Ask:

> Is the main task to copy a known template and customize it?

That is prototype factory territory.

---

## 14. Final summary

A prototype factory is a factory that creates objects by cloning preconfigured prototypes.

It is useful when objects are template-like.

Instead of repeating construction code, you keep a standard object inside the factory:

```text
executive dashboard prototype
support dashboard prototype
```

Then the factory creates new objects by copying those prototypes:

```text
clone executive dashboard prototype
set title
set region
return dashboard
```

The mental model is:

```text
Factory:
    centralize object creation

Prototype:
    create by copying an existing object

Prototype factory:
    centralize object creation by storing templates and cloning them
```

In one sentence:

> Use a prototype factory when callers should create customized copies of standard template objects without knowing how those templates are built or copied.

---

## 15. Compact version of the pattern

```python
import copy


class SomeFactory:
    _prototype_a = SomeObject(...)
    _prototype_b = SomeObject(...)

    @classmethod
    def _new_object(cls, prototype, **changes):
        result = copy.deepcopy(prototype)

        for name, value in changes.items():
            setattr(result, name, value)

        return result

    @classmethod
    def new_a(cls, **changes):
        return cls._new_object(cls._prototype_a, **changes)

    @classmethod
    def new_b(cls, **changes):
        return cls._new_object(cls._prototype_b, **changes)
```

The essence is:

```text
store prototypes
clone the right prototype
customize the clone
return it
```
