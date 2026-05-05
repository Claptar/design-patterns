---
layout: default
title: Solution 4 - Registration-Based Factory
---

# Solution 4: Registration-Based Factory

## Completed idea

The factory starts empty:

```python
class DocumentImporterFactory:
    _importers = {}
```

Importer classes register themselves:

```python
@DocumentImporterFactory.register(".md")
class MarkdownDocumentImporter(DocumentImporter):
    ...
```

Now adding a new importer does not require editing a central `if` / `elif` chain or registry dictionary inside the factory.

---

## Solution

```python
class DocumentImporterFactory:
    _importers = {}

    @classmethod
    def register(cls, extension: str):
        normalized_extension = extension.lower()

        def decorator(importer_class):
            cls._importers[normalized_extension] = importer_class
            return importer_class

        return decorator

    @classmethod
    def create_for_file(cls, path: str) -> DocumentImporter:
        suffix = Path(path).suffix.lower()

        try:
            importer_class = cls._importers[suffix]
        except KeyError:
            raise ValueError(f"Unsupported document type: {path}") from None

        return importer_class()
```

---

## Why the decorator returns the class

The decorator receives the class being decorated:

```python
@DocumentImporterFactory.register(".md")
class MarkdownDocumentImporter(DocumentImporter):
    ...
```

The decorator stores it in the registry and then returns it:

```python
def decorator(importer_class):
    cls._importers[normalized_extension] = importer_class
    return importer_class
```

Returning the class unchanged means the class name still refers to the class after decoration.

So this still works:

```python
importer = MarkdownDocumentImporter()
```

---

## How this improves the Open/Closed Principle

In Exercise 3, adding XML support required editing the factory registry:

```python
_importers = {
    ".xml": XmlDocumentImporter,
}
```

With registration, we can add a new class:

```python
@DocumentImporterFactory.register(".xml")
class XmlDocumentImporter(DocumentImporter):
    ...
```

The factory class itself does not change.

That is closer to the Open/Closed Principle.

The factory is open to new importer classes through registration.

---

## The trade-off

Registration adds indirection.

With a central registry, all supported formats are visible in one place:

```python
_importers = {
    ".txt": PlainTextDocumentImporter,
    ".md": MarkdownDocumentImporter,
    ".html": HtmlDocumentImporter,
}
```

With decorator registration, the mapping is spread across the importer classes:

```python
@DocumentImporterFactory.register(".txt")
class PlainTextDocumentImporter(...):
    ...

@DocumentImporterFactory.register(".md")
class MarkdownDocumentImporter(...):
    ...
```

That can be good because each importer owns its own registration.

But it can also make discovery harder.

There is another practical concern:

> Registration only happens if the module containing the importer class is imported.

If an importer lives in a module that is never imported, its decorator never runs, and the factory will not know about it.

---

## Discussion

This exercise shows the usual design trade-off.

A simple factory is easier to understand:

```python
if suffix == ".md":
    return MarkdownDocumentImporter()
```

A registration-based factory is easier to extend:

```python
@DocumentImporterFactory.register(".md")
class MarkdownDocumentImporter(DocumentImporter):
    ...
```

Neither is always better.

Use registration when the set of implementations changes often, or when external modules should be able to add new implementations.

Use a simple factory or registry dictionary when the set of implementations is small and stable.

---

## Final takeaway

A registration-based factory reduces the need to modify the factory when new concrete classes are added.

That makes it more open for extension.

But the extra flexibility comes with extra indirection and import/discovery concerns.

---

[Back to exercise](exercise4.md) · [Solution script](exercise4_solution.py)
