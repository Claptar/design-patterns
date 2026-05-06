---
layout: default
title: "Prototype Design Pattern"
---

# Prototype Design Pattern

## 1. What problem are we trying to solve?

Sometimes creating an object from scratch is annoying, repetitive, or expensive.

Imagine you have a report template:

```text
Monthly Sales Report
- company logo
- default layout
- theme
- standard charts
- default filters
- export settings
```

Now you need several similar reports:

```text
Monthly Sales Report - UK
Monthly Sales Report - Germany
Monthly Sales Report - Enterprise Customers
Monthly Sales Report - Trial Customers
```

Most of the configuration is the same. Only a few details change.

Without Prototype, you may keep repeating the same construction code:

```python
uk_report = Report(
    title="Monthly Sales - UK",
    theme="executive",
    charts=[...],
    filters={"region": "UK"},
    export_format="pdf",
)

germany_report = Report(
    title="Monthly Sales - Germany",
    theme="executive",
    charts=[...],
    filters={"region": "Germany"},
    export_format="pdf",
)
```

The problem is:

> I already have an object that is almost correct. Why rebuild it from zero?

That is the problem the **Prototype pattern** solves.

---

## 2. Concept introduction

The **Prototype pattern** creates new objects by copying existing objects.

Instead of saying:

```text
Create a fresh object from this class.
```

we say:

```text
Take this existing object as a prototype, clone it, then customize the clone.
```

Prototype is a **creational design pattern**.

Its main idea is:

> Create new objects by cloning existing objects.

The shape is:

```text
prototype object
      |
      | clone
      v
new object
      |
      | customize
      v
final object
```

In code, the pattern usually appears as a method like this:

```python
copy = original.clone()
```

or this:

```python
copy = original.clone(title="New title")
```

The important idea is not the method name. The important idea is:

> The existing object becomes the recipe for the new object.

---

## 3. Minimal Python example

```python
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field


@dataclass
class Chart:
    title: str
    metric: str


@dataclass
class Report:
    title: str
    theme: str
    charts: list[Chart] = field(default_factory=list)
    filters: dict[str, str] = field(default_factory=dict)
    export_format: str = "pdf"

    def clone(self, **changes) -> "Report":
        new_report = deepcopy(self)

        for name, value in changes.items():
            setattr(new_report, name, value)

        return new_report
```

Usage:

```python
base_report = Report(
    title="Monthly Sales",
    theme="executive",
    charts=[
        Chart("Revenue", "revenue"),
        Chart("New Customers", "new_customers"),
    ],
    filters={"region": "all"},
)

uk_report = base_report.clone(
    title="Monthly Sales - UK",
)

uk_report.filters["region"] = "UK"
```

Now `uk_report` starts as a copy of `base_report`, but it can be changed independently.

That is Prototype.

---

## 4. The important detail: shallow copy versus deep copy

Prototype is simple in idea, but copying is subtle.

A **shallow copy** copies only the outer object. Nested objects may still be shared.

A **deep copy** copies the outer object and nested objects.

Example problem:

```python
from copy import copy

report_a = copy(base_report)
report_b = copy(base_report)

report_a.filters["region"] = "UK"
print(report_b.filters["region"])
```

With a shallow copy, `report_a.filters` and `report_b.filters` may point to the same dictionary.
Changing one can accidentally affect the other.

That is why the earlier `clone()` method used:

```python
deepcopy(self)
```

For Prototype, always ask:

```text
Should the clone share nested objects with the original,
or should it get its own independent copies?
```

This is the most common practical issue in Prototype.

---

## 5. Natural example

A natural example is an email campaign system.

Suppose your company sends similar marketing emails:

```text
Base campaign:
- sender name
- brand theme
- tracking settings
- unsubscribe footer
- default subject style
- default delivery settings
```

Now the marketing team wants variants:

```text
Trial users campaign
Enterprise users campaign
Inactive users campaign
Black Friday campaign
```

You do not want to rebuild every campaign from scratch. You want to start from a known-good campaign template and slightly modify it.

```python
from copy import deepcopy
from dataclasses import dataclass, field


@dataclass
class EmailCampaign:
    name: str
    subject: str
    audience: str
    template: str
    tracking_enabled: bool = True
    tags: list[str] = field(default_factory=list)

    def clone(self, **changes):
        campaign = deepcopy(self)

        for field_name, value in changes.items():
            setattr(campaign, field_name, value)

        return campaign
```

Usage:

```python
base_campaign = EmailCampaign(
    name="Base Welcome Campaign",
    subject="Welcome to our product",
    audience="all_users",
    template="welcome.html",
    tags=["welcome", "onboarding"],
)

trial_campaign = base_campaign.clone(
    name="Trial Welcome Campaign",
    audience="trial_users",
)

enterprise_campaign = base_campaign.clone(
    name="Enterprise Welcome Campaign",
    audience="enterprise_users",
    subject="Welcome to your enterprise workspace",
)
```

This feels natural because campaign variants are not completely different objects.
They are modified copies of a standard template.

---

## 6. Connection to earlier learned concepts

### Prototype versus Factory

A Factory answers:

```text
Which class should I create?
```

Example:

```python
importer = ImporterFactory.create_for_file("customers.csv")
```

Prototype answers:

```text
Which existing object should I copy?
```

Example:

```python
enterprise_campaign = base_campaign.clone(audience="enterprise_users")
```

So:

```text
Factory = choose the right class.
Prototype = copy the right existing object.
```

---

### Prototype versus Builder

Builder is useful when creation is a process:

```python
request = (
    HttpRequestBuilder()
    .post(url)
    .with_auth_token(token)
    .with_json_body(body)
    .build()
)
```

Prototype is useful when creation is mostly repetition:

```python
new_report = base_report.clone(title="Monthly Sales - UK")
```

So:

```text
Builder = build step by step.
Prototype = copy a configured example.
```

---

### Prototype and Open/Closed thinking

Prototype can help when new variants should be added without changing a big conditional.

Instead of this:

```python
if campaign_type == "trial":
    ...
elif campaign_type == "enterprise":
    ...
elif campaign_type == "inactive":
    ...
```

you can keep a registry of prototypes:

```python
class CampaignPrototypeRegistry:
    def __init__(self):
        self._prototypes = {}

    def register(self, name, campaign):
        self._prototypes[name] = campaign

    def create(self, name, **changes):
        prototype = self._prototypes[name]
        return prototype.clone(**changes)
```

Usage:

```python
registry = CampaignPrototypeRegistry()

registry.register("welcome", base_campaign)

trial_campaign = registry.create(
    "welcome",
    name="Trial Welcome Campaign",
    audience="trial_users",
)
```

Now the creation rule is:

```text
Find the right prototype.
Clone it.
Customize the clone.
```

---

## 7. Example from a popular Python package

A good data-science example is `sklearn.base.clone` from scikit-learn.

In scikit-learn, `clone(estimator)` creates a new unfitted estimator with the same parameters as the original estimator.
It copies the model configuration, but not the learned fitted state.

Example:

```python
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression

prototype_model = LogisticRegression(
    C=0.5,
    max_iter=1000,
)

model_for_fold_1 = clone(prototype_model)
model_for_fold_2 = clone(prototype_model)
```

This is Prototype-like:

```text
prototype_model:
    LogisticRegression(C=0.5, max_iter=1000)

clone(prototype_model):
    new LogisticRegression with the same parameters,
    but not fitted yet
```

This matters in machine learning workflows.
For example, cross-validation needs several fresh models with the same configuration.
Each fold should get a new estimator, not reuse a model already fitted on another fold.

That is a practical Prototype idea:

> Use a configured estimator as a prototype, then create fresh independent estimators from it.

---

## 8. When to use Prototype

Use Prototype when:

| Situation | Why Prototype helps |
|---|---|
| You have many similar objects | Clone a base object instead of repeating setup. |
| Object setup is expensive or verbose | Configure once, then copy. |
| You need template-like objects | Store standard prototypes and create variants. |
| The exact class may not matter to the caller | The caller can clone an object without knowing how to build it. |
| Runtime configuration matters | Users or config files can define prototypes dynamically. |
| You want fresh objects with the same configuration | Common in ML estimators, simulations, workflows, reports, and templates. |

Good examples:

```text
report templates
email campaign templates
game enemy templates
configured ML estimators
workflow/task templates
document/page templates
chart templates
```

---

## 9. When not to use Prototype

Do not use Prototype when normal construction is already clear.

```python
point = Point(x=10, y=20)
```

This does not need:

```python
point = point_prototype.clone(x=10, y=20)
```

Avoid Prototype when copying is dangerous or unclear.

Examples:

```text
database connections
open files
network sockets
thread locks
objects with unique IDs
objects with security tokens
objects with hidden mutable state
```

Also avoid it when deep copying would be too expensive.

If the object contains a huge dataset, cloning the whole thing may be wasteful.
In that case, you may need a custom `clone()` method that copies configuration but shares or resets heavy data intentionally.

---

## 10. Practical rule of thumb

Ask:

> Do I already have an object that is almost the object I need?

If yes, Prototype may help.

Ask:

> Would rebuilding this object from scratch repeat a lot of setup?

If yes, Prototype may help.

Ask:

> Is it obvious which parts should be shared and which parts should be copied?

If no, be careful.
Define a custom `clone()` method instead of blindly using `copy.copy()` or `copy.deepcopy()`.

The best practical rule:

> Use Prototype when "copy this configured example and adjust a few fields" is clearer than "construct a new object from scratch."

---

## 11. Summary and mental model

Prototype is a creational design pattern for making new objects by cloning existing ones.

It is useful when objects have template-like configuration:

```text
Start with this known-good object.
Make a copy.
Change only what is different.
```

Mental model:

```text
Factory:   choose the right class.
Builder:   assemble the object step by step.
Prototype: copy an existing object and customize the copy.
```

One sentence:

> Prototype is useful when an existing configured object is the clearest recipe for creating the next object.
