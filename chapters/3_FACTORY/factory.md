---
layout: default
title: Factories
---

# Factories

## 1. Starting from factory methods

A factory method is a method that creates and returns an object.

One common use of factory methods is as **named constructors**.

For example:

```python
money = Money.from_dollars(12.99, "USD")
point = Point.from_polar(5, 0.927)
```

These methods are useful because the normal constructor does not always clearly explain how the object is being created.

This is unclear:

```python
money = Money(1299, "USD")
```

Does `1299` mean dollars, cents, or some other minor unit?

This is clearer:

```python
money = Money.from_cents(1299, "USD")
```

This is also unclear:

```python
point = Point(5, 0.927)
```

Are those Cartesian coordinates, or polar coordinates?

This is clearer:

```python
point = Point.from_polar(5, 0.927)
```

In these examples, the factory method belongs naturally on the class itself.

```text
Money knows how to create Money from dollars.
Point knows how to create Point from polar coordinates.
```

So a simple rule is:

> If a class has several natural ways to create itself, factory methods can make those construction paths explicit.

But sometimes creation logic grows beyond one class.

That is where factories become useful.

---

## 2. When factory methods stop being enough

Imagine an application that imports customer data.

The input file might be:

```text
customers.csv
customers.json
customers.xlsx
```

Each file format needs different parsing logic.

A CSV file needs a CSV importer:

```python
CsvCustomerImporter
```

A JSON file needs a JSON importer:

```python
JsonCustomerImporter
```

An Excel file needs an Excel importer:

```python
ExcelCustomerImporter
```

Now ask:

> Where should this creation logic live?

We could try to put a factory method on one of the concrete importer classes:

```python
CsvCustomerImporter.from_file(path)
```

But that feels wrong.

Why should `CsvCustomerImporter` decide what to do with a JSON file?

```python
CsvCustomerImporter.from_file("customers.json")
```

That would be strange.

We could put the logic on a base class:

```python
CustomerImporter.from_file(path)
```

That is better, but now the base class may need to know about all of its concrete implementations:

```text
CustomerImporter knows about CsvCustomerImporter.
CustomerImporter knows about JsonCustomerImporter.
CustomerImporter knows about ExcelCustomerImporter.
```

Sometimes that is acceptable.

But often, creation has become its own responsibility.

The question is no longer:

```text
How does this class create itself from this input?
```

The question is now:

```text
Given this situation, which class should be created?
```

That is the point where a factory becomes natural.

---

## 3. The problem without a factory

A naive implementation might look like this:

```python
if path.endswith(".csv"):
    importer = CsvCustomerImporter()
elif path.endswith(".json"):
    importer = JsonCustomerImporter()
elif path.endswith(".xlsx"):
    importer = ExcelCustomerImporter()
else:
    raise ValueError("Unsupported file type")

customers = importer.import_customers(path)
```

This is fine in one place.

The problem starts when the same decision appears in many places.

```python
# admin_upload.py
if path.endswith(".csv"):
    importer = CsvCustomerImporter()
elif path.endswith(".json"):
    importer = JsonCustomerImporter()

# nightly_sync.py
if path.endswith(".csv"):
    importer = CsvCustomerImporter()
elif path.endswith(".json"):
    importer = JsonCustomerImporter()

# migration_tool.py
if path.endswith(".csv"):
    importer = CsvCustomerImporter()
elif path.endswith(".json"):
    importer = JsonCustomerImporter()
```

Now the creation rule is scattered.

The mapping is repeated:

```text
.csv  -> CsvCustomerImporter
.json -> JsonCustomerImporter
.xlsx -> ExcelCustomerImporter
```

If we later add XML support, we may need to update several files.

The issue is not that `if` statements are bad.

The issue is that the same object-creation decision has no single home.

---

## 4. Factory

A **factory** is an object, function, or class whose job is to create other objects.

In this context, a factory answers this question:

> Given this situation, which concrete object should I create?

So instead of this:

```python
if path.endswith(".csv"):
    importer = CsvCustomerImporter()
elif path.endswith(".json"):
    importer = JsonCustomerImporter()
elif path.endswith(".xlsx"):
    importer = ExcelCustomerImporter()
```

we write this:

```python
importer = CustomerImporterFactory.create_for_file(path)
```

The caller says:

```text
Give me an importer for this file.
```

The factory decides:

```text
This is a .csv file, so create CsvCustomerImporter.
```

That is the core idea.

A factory is a natural extension of factory methods.

| Idea | Main question | Example |
|---|---|---|
| Factory method as named constructor | How should this class create itself from this input? | `Point.from_polar(...)` |
| Factory | Which class should be created for this situation? | `CustomerImporterFactory.create_for_file(...)` |

---

## 5. Importer example

First, define a common interface.

```python
from abc import ABC, abstractmethod


class CustomerImporter(ABC):
    @abstractmethod
    def import_customers(self, path: str) -> list[dict]:
        pass
```

Now define concrete importers.

```python
import csv
import json


class CsvCustomerImporter(CustomerImporter):
    def import_customers(self, path: str) -> list[dict]:
        with open(path, newline="") as file:
            return list(csv.DictReader(file))


class JsonCustomerImporter(CustomerImporter):
    def import_customers(self, path: str) -> list[dict]:
        with open(path) as file:
            return json.load(file)


class ExcelCustomerImporter(CustomerImporter):
    def import_customers(self, path: str) -> list[dict]:
        # Pretend this uses an Excel library.
        print(f"Reading Excel file: {path}")
        return []
```

Now the factory owns the creation decision.

```python
class CustomerImporterFactory:
    @staticmethod
    def create_for_file(path: str) -> CustomerImporter:
        normalized_path = path.lower()

        if normalized_path.endswith(".csv"):
            return CsvCustomerImporter()

        if normalized_path.endswith(".json"):
            return JsonCustomerImporter()

        if normalized_path.endswith(".xlsx"):
            return ExcelCustomerImporter()

        raise ValueError(f"Unsupported customer file type: {path}")
```

Usage:

```python
importer = CustomerImporterFactory.create_for_file("customers.csv")
customers = importer.import_customers("customers.csv")
```

The caller does not need to know which concrete importer is being used.

It only needs to know that it has a `CustomerImporter`.

---

## 6. What changed compared with factory methods?

With a named constructor, the class creates itself.

```python
point = Point.from_polar(5, 0.927)
```

The relationship is simple:

```text
Point.from_polar(...) returns Point.
```

With a factory, the factory may return one of several related classes.

```python
importer = CustomerImporterFactory.create_for_file(path)
```

The result might be:

```text
CsvCustomerImporter
JsonCustomerImporter
ExcelCustomerImporter
```

The caller does not care which one, as long as it behaves like a `CustomerImporter`.

So the purpose has shifted.

Factory method:

```text
Make construction of one class clearer.
```

Factory:

```text
Centralize the decision about which implementation to create.
```

---

## 7. Why not direct construction?

Direct construction is still fine when the caller really does want a specific class.

For example, in a test for the CSV importer:

```python
importer = CsvCustomerImporter()
```

That is clear.

We specifically want the CSV implementation.

But application code often knows only the situation:

```python
path = uploaded_file.path
```

It does not want to say:

```python
importer = CsvCustomerImporter()
```

because the uploaded file might not be CSV.

The application code wants to say:

```python
importer = CustomerImporterFactory.create_for_file(path)
```

That means:

```text
Choose the correct importer for this file.
```

That is a more useful abstraction.

---

## 8. A factory can be a function

In Python, a factory does not always need to be a class.

A simple function is often enough.

```python
def create_customer_importer(path: str) -> CustomerImporter:
    normalized_path = path.lower()

    if normalized_path.endswith(".csv"):
        return CsvCustomerImporter()

    if normalized_path.endswith(".json"):
        return JsonCustomerImporter()

    if normalized_path.endswith(".xlsx"):
        return ExcelCustomerImporter()

    raise ValueError(f"Unsupported customer file type: {path}")
```

Usage:

```python
importer = create_customer_importer(path)
customers = importer.import_customers(path)
```

This is still a factory.

The important idea is not the class named `Factory`.

The important idea is:

```text
Object creation logic has one clear place to live.
```

In Python, prefer the simplest shape that communicates the idea.

If a function is enough, use a function.

If we need shared configuration, state, dependencies, or registration, a factory class may become useful.

---

## 9. A registry version

For a small number of cases, `if` / `elif` is readable.

But if the mapping grows, a registry can be cleaner.

```python
class CustomerImporterFactory:
    _importers = {
        ".csv": CsvCustomerImporter,
        ".json": JsonCustomerImporter,
        ".xlsx": ExcelCustomerImporter,
    }

    @classmethod
    def create_for_file(cls, path: str) -> CustomerImporter:
        normalized_path = path.lower()

        for extension, importer_class in cls._importers.items():
            if normalized_path.endswith(extension):
                return importer_class()

        raise ValueError(f"Unsupported customer file type: {path}")
```

Now the mapping is visible in one place:

```python
_importers = {
    ".csv": CsvCustomerImporter,
    ".json": JsonCustomerImporter,
    ".xlsx": ExcelCustomerImporter,
}
```

That is exactly the decision the factory owns.

---

## 10. When factories are worth using

Use a factory when object creation involves a meaningful choice.

```python
importer = CustomerImporterFactory.create_for_file(path)
```

The file type determines which importer should be created.

Use a factory when the same creation logic would otherwise be repeated.

```python
if provider == "stripe":
    processor = StripePaymentProcessor()
elif provider == "paypal":
    processor = PayPalPaymentProcessor()
```

If this appears in several places, move it into a factory.

Use a factory when callers should depend on an abstraction.

```python
importer: CustomerImporter
```

The caller should not need to care whether it receives a CSV importer, JSON importer, or Excel importer.

Use a factory when creation rules may change.

Today the rule may be simple:

```text
.csv -> CsvCustomerImporter
```

Later it might depend on configuration, tenant settings, feature flags, or installed plugins.

A factory gives that changing logic one place to live.

---

## 11. When factories are too much

Do not use a factory when the constructor is already obvious.

```python
point = Point(x=10, y=20)
```

This would be unnecessary:

```python
point = PointFactory.create(10, 20)
```

The factory adds a layer without adding meaning.

Do not use a factory when there is only one implementation and no meaningful creation logic.

```python
class UserFactory:
    @staticmethod
    def create(name, email):
        return User(name, email)
```

Usage:

```python
user = UserFactory.create("Alice", "alice@example.com")
```

If the factory only repeats the constructor, prefer the constructor.

```python
user = User("Alice", "alice@example.com")
```

Also avoid factories with vague names.

```python
thing = ThingFactory.create(data)
```

If the reader cannot tell what kind of decision is being made, the factory may make the design more mysterious.

A better factory method name explains the decision:

```python
importer = CustomerImporterFactory.create_for_file(path)
processor = PaymentProcessorFactory.create_for_provider(provider)
```

The value is not just in hiding construction.

The value is in naming the creation decision.

---

## 12. Practical rule of thumb

Ask:

> Does this class simply need clearer ways to create itself?

Use factory methods as named constructors.

```python
Money.from_dollars(12.99, "USD")
Point.from_polar(5, 0.927)
```

Ask:

> Does the program need to choose between several related concrete classes?

Use a factory.

```python
CustomerImporterFactory.create_for_file(path)
```

Ask:

> Is this creation decision repeated in more than one place?

A factory may help.

Ask:

> Am I just wrapping a constructor?

The factory is probably unnecessary.

---

## 13. Final summary

Factory methods and factories are closely related, but they solve different levels of the creation problem.

A factory method as a named constructor is useful when one class has multiple clear ways to create itself.

```python
Point.from_cartesian(2, 3)
Point.from_polar(5, 0.927)
```

A factory is useful when the program must choose between several related concrete classes.

```python
CustomerImporterFactory.create_for_file("customers.csv")
```

A good factory can:

- centralize object creation decisions
- remove repeated creation conditionals
- hide concrete implementation classes from callers
- let callers depend on a common interface
- make runtime creation rules easier to change
- give a meaningful name to a creation decision

In one sentence:

> Factory methods name different ways for a class to create itself; factories centralize the decision of which related class should be created for a given situation.

---

[Factory Methods as Named Constructors](factory_methods_named_constructors_note.md) · [Factories and the Open/Closed Principle](factories_and_open_closed_principle_note.md)

