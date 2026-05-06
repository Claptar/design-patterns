---
layout: default
title: Exercise 4 - Dashboard Prototype Factory
---

# Exercise 4: Dashboard Prototype Factory

## Goal

Practice combining Prototype with Factory.

The factory should choose a preconfigured dashboard prototype, clone it, customize it, and return the new dashboard.

---

## Story

Your company now has two standard dashboard templates:

```text
sales dashboard
marketing dashboard
```

Each one has different widgets and default filters.

Callers should not manually clone those templates. They should use a clear factory method:

```python
dashboard = DashboardFactory.new_sales_dashboard(
    title="UK Sales Dashboard",
    owner="Alice",
    region="UK",
)
```

The caller should not know the street-level details of the prototype:

- which widgets the sales dashboard has,
- which filters start with default values,
- how clone rules work,
- how the data source is shared,
- how cache is reset.

---

## Your task

Open `exercise4.py` and implement `DashboardFactory`.

The `Dashboard.clone()` method is already implemented from the previous exercise.

Implement:

```python
@classmethod
def _new_dashboard(cls, prototype, title, owner, region):
    ...
```

Then implement:

```python
@classmethod
def new_sales_dashboard(cls, title, owner, region):
    ...

@classmethod
def new_marketing_dashboard(cls, title, owner, region):
    ...
```

---

## Required behavior

The factory should:

1. pick the right prototype,
2. clone it,
3. set the title,
4. set the owner,
5. set the region filter,
6. return the customized dashboard.

---

## Tests to satisfy

Run:

```bash
python exercise4.py
```

The tests check that:

- sales dashboards use the sales prototype,
- marketing dashboards use the marketing prototype,
- cloned dashboards are independent from each other,
- prototypes are not mutated,
- the shared data source rule still holds.

---

## Mental model

```text
DashboardFactory
    sales_dashboard prototype
    marketing_dashboard prototype

new_sales_dashboard(...)
    clone sales prototype
    customize title, owner, region

new_marketing_dashboard(...)
    clone marketing prototype
    customize title, owner, region
```

This is the same idea as a prototype factory:

```text
choose prototype -> clone -> customize -> return
```
