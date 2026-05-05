---
layout: default
title: Factories and the Open/Closed Principle
---

# Factories and the Open/Closed Principle

## 1. The concern

Previously, we used an example like this:

```python
class CustomerImporterFactory:
    @staticmethod
    def create_for_file(path: str) -> CustomerImporter:
        if path.endswith(".csv"):
            return CsvCustomerImporter()

        if path.endswith(".json"):
            return JsonCustomerImporter()

        if path.endswith(".xlsx"):
            return ExcelCustomerImporter()

        raise ValueError(f"Unsupported customer file type: {path}")
```

This is a simple factory.

It centralizes object creation.

Instead of repeating this logic in many places:

```python
if path.endswith(".csv"):
    importer = CsvCustomerImporter()
elif path.endswith(".json"):
    importer = JsonCustomerImporter()
elif path.endswith(".xlsx"):
    importer = ExcelCustomerImporter()
```

we can write:

```python
importer = CustomerImporterFactory.create_for_file(path)
```

That is an improvement.

But there is a real concern:

> Does this factory break the Open/Closed Principle?

The answer is:

> Yes, in the strict sense, a simple `if` / `elif` factory usually breaks the Open/Closed Principle.

---

## 2. Why it breaks the Open/Closed Principle

The Open/Closed Principle says:

> Software entities should be open for extension, but closed for modification.

In other words, we should be able to add new behavior without constantly modifying existing code.

Now imagine we want to add XML support.

We create a new importer:

```python
class XmlCustomerImporter(CustomerImporter):
    def import_customers(self, path: str) -> list[dict]:
        ...
```

But this is not enough.

We also have to modify the factory:

```python
class CustomerImporterFactory:
    @staticmethod
    def create_for_file(path: str) -> CustomerImporter:
        if path.endswith(".csv"):
            return CsvCustomerImporter()

        if path.endswith(".json"):
            return JsonCustomerImporter()

        if path.endswith(".xlsx"):
            return ExcelCustomerImporter()

        if path.endswith(".xml"):
            return XmlCustomerImporter()

        raise ValueError(f"Unsupported customer file type: {path}")
```

The factory had to be changed.

So the factory is not closed for modification.

That is the Open/Closed Principle problem.

---

## 3. Does that mean the factory is useless?

No.

This is the important nuance.

A simple factory may not fully satisfy the Open/Closed Principle, but it can still improve the design.

Without a factory, the creation decision may be scattered across many files:

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

If we add XML support, we may need to modify several files.

With a factory, the creation decision is centralized:

```python
importer = CustomerImporterFactory.create_for_file(path)
```

Now XML support may require changing only one place.

So the simple factory gives us:

```text
not perfect Open/Closed Principle,
but better containment of change.
```

That is still valuable.

The factory localizes the violation.

Instead of many files knowing the mapping:

```text
.csv  -> CsvCustomerImporter
.json -> JsonCustomerImporter
.xlsx -> ExcelCustomerImporter
```

one factory knows it.

---

## 4. The consequence of a simple factory

The main consequence is that the factory becomes a place we must edit every time a new implementation is added.

For a small, stable set of choices, this is often acceptable.

For example:

```text
.csv
.json
.xlsx
```

If these are the only supported formats and they rarely change, a simple factory is easy to understand.

But if new importers are added often, the factory can become a bottleneck.

Every new importer requires us to:

1. create the new importer class
2. open the factory
3. edit the conditional
4. retest the factory logic

The factory also becomes coupled to every concrete importer.

```text
CustomerImporterFactory knows about CsvCustomerImporter.
CustomerImporterFactory knows about JsonCustomerImporter.
CustomerImporterFactory knows about ExcelCustomerImporter.
CustomerImporterFactory knows about XmlCustomerImporter.
```

As the list grows, the factory can become a central object that knows too much.

That is the design pressure that pushes us toward more flexible factory designs.

---

## 5. First workaround: registry dictionary

A small improvement is to replace the `if` / `elif` chain with a registry dictionary.

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

Now the mapping is explicit:

```python
_importers = {
    ".csv": CsvCustomerImporter,
    ".json": JsonCustomerImporter,
    ".xlsx": ExcelCustomerImporter,
}
```

This is easier to scan than a long conditional.

It says clearly:

```text
.csv  -> CsvCustomerImporter
.json -> JsonCustomerImporter
.xlsx -> ExcelCustomerImporter
```

However, this still does not fully solve the Open/Closed Principle problem.

If we add XML support, we still modify the registry:

```python
_importers = {
    ".csv": CsvCustomerImporter,
    ".json": JsonCustomerImporter,
    ".xlsx": ExcelCustomerImporter,
    ".xml": XmlCustomerImporter,
}
```

So a registry dictionary improves readability and organization, but it does not completely remove the need to modify the factory.

It is a cleaner shape, not a complete Open/Closed Principle solution.

---

## 6. Better workaround: explicit registration

To get closer to the Open/Closed Principle, we can allow importers to be registered from the outside.

```python
class CustomerImporterFactory:
    _importers = {}

    @classmethod
    def register(cls, extension: str, importer_class: type[CustomerImporter]):
        cls._importers[extension] = importer_class

    @classmethod
    def create_for_file(cls, path: str) -> CustomerImporter:
        normalized_path = path.lower()

        for extension, importer_class in cls._importers.items():
            if normalized_path.endswith(extension):
                return importer_class()

        raise ValueError(f"Unsupported customer file type: {path}")
```

Now importers can be registered separately:

```python
CustomerImporterFactory.register(".csv", CsvCustomerImporter)
CustomerImporterFactory.register(".json", JsonCustomerImporter)
CustomerImporterFactory.register(".xlsx", ExcelCustomerImporter)
```

Adding XML support becomes:

```python
class XmlCustomerImporter(CustomerImporter):
    def import_customers(self, path: str) -> list[dict]:
        ...
```

and then:

```python
CustomerImporterFactory.register(".xml", XmlCustomerImporter)
```

The factory class itself does not need to change.

That is closer to the Open/Closed Principle.

The factory is open to new importer types through registration.

---

## 7. Decorator-based registration

In Python, explicit registration can be made more convenient with a decorator.

```python
class CustomerImporterFactory:
    _importers = {}

    @classmethod
    def register(cls, extension: str):
        def decorator(importer_class):
            cls._importers[extension] = importer_class
            return importer_class

        return decorator

    @classmethod
    def create_for_file(cls, path: str) -> CustomerImporter:
        normalized_path = path.lower()

        for extension, importer_class in cls._importers.items():
            if normalized_path.endswith(extension):
                return importer_class()

        raise ValueError(f"Unsupported customer file type: {path}")
```

Now concrete importers can register themselves:

```python
@CustomerImporterFactory.register(".csv")
class CsvCustomerImporter(CustomerImporter):
    def import_customers(self, path: str) -> list[dict]:
        ...


@CustomerImporterFactory.register(".json")
class JsonCustomerImporter(CustomerImporter):
    def import_customers(self, path: str) -> list[dict]:
        ...


@CustomerImporterFactory.register(".xlsx")
class ExcelCustomerImporter(CustomerImporter):
    def import_customers(self, path: str) -> list[dict]:
        ...
```

Adding a new importer does not require editing the factory:

```python
@CustomerImporterFactory.register(".xml")
class XmlCustomerImporter(CustomerImporter):
    def import_customers(self, path: str) -> list[dict]:
        ...
```

The factory knows how to create importers, but it does not need to know every importer in advance.

That is much more open for extension.

---

## 8. The trade-off of registration

Registration is more flexible, but it adds complexity.

With the simple factory, everything is visible in one place:

```python
if path.endswith(".csv"):
    return CsvCustomerImporter()

if path.endswith(".json"):
    return JsonCustomerImporter()
```

With registration, the mapping is spread across classes:

```python
@CustomerImporterFactory.register(".csv")
class CsvCustomerImporter(CustomerImporter):
    ...
```

This can be good or bad.

It is good because each importer owns its own registration.

It can be bad because it is less obvious where all supported formats are listed.

There is also an important practical issue:

> Registration only happens if the module containing the importer has been imported.

For example, if `XmlCustomerImporter` lives in `xml_importer.py`, but that module is never imported, then this code never runs:

```python
@CustomerImporterFactory.register(".xml")
class XmlCustomerImporter(CustomerImporter):
    ...
```

So registration systems often need an import or discovery mechanism.

That is why this approach is useful for larger systems or plugin-like systems, but may be overkill for small applications.

---

## 9. Another workaround: dependency injection

Another approach is to move the mapping outside the factory.

```python
class CustomerImporterFactory:
    def __init__(self, importers: dict[str, type[CustomerImporter]]):
        self._importers = importers

    def create_for_file(self, path: str) -> CustomerImporter:
        normalized_path = path.lower()

        for extension, importer_class in self._importers.items():
            if normalized_path.endswith(extension):
                return importer_class()

        raise ValueError(f"Unsupported customer file type: {path}")
```

Now the factory does not decide which importers exist.

It receives that information from the outside:

```python
factory = CustomerImporterFactory({
    ".csv": CsvCustomerImporter,
    ".json": JsonCustomerImporter,
    ".xlsx": ExcelCustomerImporter,
})
```

Adding XML support changes the composition or configuration code:

```python
factory = CustomerImporterFactory({
    ".csv": CsvCustomerImporter,
    ".json": JsonCustomerImporter,
    ".xlsx": ExcelCustomerImporter,
    ".xml": XmlCustomerImporter,
})
```

The factory class itself remains unchanged.

This is useful when the set of implementations depends on configuration, environment, or tests.

For example, in tests we could provide a fake importer:

```python
factory = CustomerImporterFactory({
    ".csv": FakeCustomerImporter,
})
```

This improves testability and reduces hardcoded dependencies inside the factory.

---

## 10. Which version should we use?

For a small, stable set of choices, use the simple version.

```python
if path.endswith(".csv"):
    return CsvCustomerImporter()
elif path.endswith(".json"):
    return JsonCustomerImporter()
```

It is direct and easy to understand.

For a slightly larger set, use a registry dictionary.

```python
_importers = {
    ".csv": CsvCustomerImporter,
    ".json": JsonCustomerImporter,
    ".xlsx": ExcelCustomerImporter,
}
```

This makes the mapping clearer.

For a system where new implementations are added often, use registration.

```python
@CustomerImporterFactory.register(".xml")
class XmlCustomerImporter(CustomerImporter):
    ...
```

This lets the factory stay unchanged when new importers are added.

For an application where creation rules should come from configuration, use dependency injection.

```python
factory = CustomerImporterFactory(importers=configured_importers)
```

This keeps the factory generic and moves the concrete setup to the application boundary.

---

## 11. The realistic conclusion

A simple factory with `if` / `elif` does violate the Open/Closed Principle in the strict sense.

But it may still be a good design because it improves the situation from this:

```text
Creation logic scattered across many files.
```

to this:

```text
Creation logic centralized in one file.
```

That is often a worthwhile first step.

Then, if the factory starts changing too often, we can evolve it:

```text
if / elif factory
    -> registry dictionary
    -> explicit registration
    -> plugin discovery or dependency injection
```

Do not start with the most flexible solution unless the problem needs it.

More flexibility usually means more indirection.

More indirection means the code can become harder to follow.

---

## 12. Practical rule of thumb

Ask:

> Is the set of concrete types small and stable?

A simple factory is probably fine.

Ask:

> Is the factory changing every time a new feature is added?

Consider a registry or registration mechanism.

Ask:

> Do external modules or plugins need to add new implementations?

Use registration or plugin discovery.

Ask:

> Should the available implementations depend on configuration or tests?

Use dependency injection.

The important idea is:

> A simple factory may not satisfy the Open/Closed Principle perfectly, but it can still reduce the damage by localizing change. Use more flexible factory designs only when the rate of change justifies the extra complexity.

---

## 13. Final summary

Factories centralize object creation decisions.

A simple factory often uses `if` / `elif` logic or a dictionary to choose between concrete classes.

That is useful because it keeps creation logic out of the rest of the application.

However, a simple factory usually violates the Open/Closed Principle because adding a new concrete type requires modifying the factory.

This is not always a problem.

For small and stable sets of choices, a simple factory is often the clearest solution.

For larger or frequently changing systems, we can move toward more extensible designs:

- registry dictionaries
- explicit registration
- decorator-based registration
- dependency injection
- plugin discovery

In one sentence:

> A simple factory centralizes change; a more extensible factory reduces the need to modify the factory when new implementations are added.

---

[Factories](factory.md)

