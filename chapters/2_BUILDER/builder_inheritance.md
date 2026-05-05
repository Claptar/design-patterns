---
layout: default
title: Builder Inheritance
---

# Builder Inheritance

## 1. What is builder inheritance?

**Builder inheritance** is a Builder-pattern variation used when the object you are building has inheritance, and you want builders for subclasses to reuse builder steps from builders for base classes.

In plain English:

> If `Employee` inherits from `Person`, then `EmployeeBuilder` should be able to reuse person-building methods like `.named(...)` and `.aged(...)`, while adding employee-specific methods like `.works_as(...)` and `.earning(...)`.

---

## 2. The problem

Suppose you have these classes:

```python
from dataclasses import dataclass


@dataclass
class Person:
    name: str | None = None
    age: int | None = None


@dataclass
class Employee(Person):
    position: str | None = None
    salary: int | None = None
```

A simple `PersonBuilder` might look like this:

```python
class PersonBuilder:
    def __init__(self):
        self.person = Person()

    def named(self, name):
        self.person.name = name
        return self

    def aged(self, age):
        self.person.age = age
        return self

    def build(self):
        return self.person
```

Usage:

```python
person = (
    PersonBuilder()
    .named("Alice")
    .aged(30)
    .build()
)
```

So far, fine.

Now suppose you need an `EmployeeBuilder`.

A naive version might duplicate the person-building methods:

```python
class EmployeeBuilder:
    def __init__(self):
        self.employee = Employee()

    def named(self, name):
        self.employee.name = name
        return self

    def aged(self, age):
        self.employee.age = age
        return self

    def works_as(self, position):
        self.employee.position = position
        return self

    def earning(self, salary):
        self.employee.salary = salary
        return self

    def build(self):
        return self.employee
```

This works, but `named()` and `aged()` are duplicated.

That is the problem builder inheritance tries to solve.

---

## 3. First attempt: inherit the builder

You might write:

```python
class EmployeeBuilder(PersonBuilder):
    def __init__(self):
        self.person = Employee()

    def works_as(self, position):
        self.person.position = position
        return self

    def earning(self, salary):
        self.person.salary = salary
        return self
```

Now this works:

```python
employee = (
    EmployeeBuilder()
    .named("Alice")
    .aged(30)
    .works_as("Engineer")
    .earning(100_000)
    .build()
)
```

`EmployeeBuilder` inherits `.named()` and `.aged()` from `PersonBuilder`, and those methods return `self`.

Since `self` is actually an `EmployeeBuilder`, the chain can continue with `.works_as(...)` and `.earning(...)`.

That is the basic idea.

---

## 4. The subtle problem in statically typed languages

In dynamic languages like Python, the simple version often works at runtime.

But in statically typed languages such as Java, C#, TypeScript, or Kotlin, fluent chaining can break.

For example, conceptually:

```java
Employee employee = new EmployeeBuilder()
    .named("Alice")
    .worksAs("Engineer")
    .build();
```

The problem is that `.named("Alice")` may be declared to return `PersonBuilder`.

So after calling `.named(...)`, the compiler thinks the chain is a `PersonBuilder`, not an `EmployeeBuilder`.

That means `.worksAs(...)` may not be available.

The issue is:

```text
Base builder methods return the base builder type.
Subclass builder methods exist only on the subclass builder type.
```

So the chain can collapse back to the parent builder type.

---

## 5. The solution: self types / recursive generics

In statically typed languages, builder inheritance often uses a technique called:

```text
self types
recursive generics
curiously recurring template pattern
CRTP
```

The idea is:

> Base builder methods should return the concrete child builder type, not just the base builder type.

Java-like pseudocode:

```java
class PersonBuilder<TSelf extends PersonBuilder<TSelf>> {
    protected Person person = new Person();

    public TSelf named(String name) {
        person.name = name;
        return self();
    }

    public TSelf aged(int age) {
        person.age = age;
        return self();
    }

    protected TSelf self() {
        return (TSelf) this;
    }

    public Person build() {
        return person;
    }
}
```

Then:

```java
class EmployeeBuilder extends PersonBuilder<EmployeeBuilder> {
    public EmployeeBuilder worksAs(String position) {
        ((Employee) person).position = position;
        return this;
    }
}
```

Now this works:

```java
new EmployeeBuilder()
    .named("Alice")
    .aged(30)
    .worksAs("Engineer");
```

Because `.named()` returns `EmployeeBuilder`, not merely `PersonBuilder`.

---

## 6. Python version with `Self`

Python does not need recursive generics for runtime behavior, but type hints can still benefit from `Self`.

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Self


@dataclass
class Person:
    name: str | None = None
    age: int | None = None


@dataclass
class Employee(Person):
    position: str | None = None
    salary: int | None = None
```

Base builder:

```python
class PersonBuilder:
    def __init__(self):
        self.person = Person()

    def named(self, name: str) -> Self:
        self.person.name = name.strip()
        return self

    def aged(self, age: int) -> Self:
        if age < 0:
            raise ValueError("Age cannot be negative")

        self.person.age = age
        return self

    def build(self) -> Person:
        if not self.person.name:
            raise ValueError("Name is required")

        return self.person
```

Subclass builder:

```python
class EmployeeBuilder(PersonBuilder):
    def __init__(self):
        self.person = Employee()

    def works_as(self, position: str) -> Self:
        self.person.position = position.strip()
        return self

    def earning(self, salary: int) -> Self:
        if salary < 0:
            raise ValueError("Salary cannot be negative")

        self.person.salary = salary
        return self

    def build(self) -> Employee:
        employee = super().build()

        if not isinstance(employee, Employee):
            raise TypeError("Expected Employee")

        if not employee.position:
            raise ValueError("Position is required")

        return employee
```

Usage:

```python
employee = (
    EmployeeBuilder()
    .named("Alice")
    .aged(30)
    .works_as("Engineer")
    .earning(100_000)
    .build()
)
```

The inherited methods `.named()` and `.aged()` return `Self`, so a type checker understands that the chain is still an `EmployeeBuilder`.

---

## 7. What builder inheritance buys you

Builder inheritance lets you reuse construction steps from parent objects.

```text
PersonBuilder
  named()
  aged()

EmployeeBuilder
  inherits named()
  inherits aged()
  adds works_as()
  adds earning()
```

So you avoid duplication.

This is useful when the object model itself has a real inheritance hierarchy:

```text
Person -> Employee
Vehicle -> Car
Message -> EmailMessage
CloudResource -> VirtualMachine
Document -> PdfDocument
```

The builder hierarchy can mirror the object hierarchy.

---

## 8. Another example: message builders

Suppose you have a base message:

```python
from dataclasses import dataclass, field
from typing import Self


@dataclass
class Message:
    recipient: str | None = None
    subject: str | None = None


@dataclass
class EmailMessage(Message):
    html_body: str | None = None
    cc: list[str] = field(default_factory=list)
```

A base builder can handle common message fields:

```python
class MessageBuilder:
    def __init__(self):
        self.message = Message()

    def to(self, recipient: str) -> Self:
        self.message.recipient = recipient.strip().lower()
        return self

    def subject(self, subject: str) -> Self:
        self.message.subject = subject.strip()
        return self

    def build(self) -> Message:
        if not self.message.recipient:
            raise ValueError("Recipient is required")

        if not self.message.subject:
            raise ValueError("Subject is required")

        return self.message
```

Then the email builder adds email-specific steps:

```python
class EmailMessageBuilder(MessageBuilder):
    def __init__(self):
        self.message = EmailMessage()

    def html(self, html_body: str) -> Self:
        self.message.html_body = html_body
        return self

    def cc(self, recipient: str) -> Self:
        self.message.cc.append(recipient.strip().lower())
        return self

    def build(self) -> EmailMessage:
        email = super().build()

        if not isinstance(email, EmailMessage):
            raise TypeError("Expected EmailMessage")

        if not email.html_body:
            raise ValueError("HTML body is required")

        return email
```

Usage:

```python
email = (
    EmailMessageBuilder()
    .to("customer@example.com")
    .subject("Your invoice")
    .html("<p>Thanks for your purchase.</p>")
    .cc("accounts@example.com")
    .build()
)
```

The email builder reuses common message-building steps and adds email-specific ones.

---

## 9. When builder inheritance is useful

Use it when:

```text
the final objects use inheritance
subclasses share construction steps
subclasses add their own construction steps
you want fluent chaining to work across inherited builder methods
you want to avoid duplicating builder methods
```

Good fit:

```text
PersonBuilder -> EmployeeBuilder
VehicleBuilder -> CarBuilder
NotificationBuilder -> EmailNotificationBuilder
CloudResourceBuilder -> VirtualMachineBuilder
DocumentBuilder -> PdfDocumentBuilder
```

---

## 10. When builder inheritance is too much

Avoid builder inheritance when there is no real inheritance relationship.

Bad example:

```python
class ReportBuilder:
    ...


class InvoiceBuilder(ReportBuilder):
    ...
```

Only do this if an invoice really is a kind of report and should inherit the same construction contract.

Also avoid builder inheritance if the hierarchy gets too deep:

```text
BaseBuilder
  DocumentBuilder
    SignedDocumentBuilder
      PdfSignedDocumentBuilder
        EncryptedPdfSignedDocumentBuilder
```

That becomes hard to reason about.

When the builder hierarchy starts getting complicated, composition is often cleaner than inheritance.

For example, builder facets may be better:

```python
builder.security.enable_encryption()
builder.signing.signed_by(...)
builder.format.pdf()
```

Instead of a deep subclass chain.

---

## 11. Builder inheritance versus builder facets

They solve different problems.

| Pattern variation   | Use when                                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------------ |
| Builder inheritance | Your final objects have an inheritance hierarchy and builders should reuse parent builder steps. |
| Builder facets      | One complex object has distinct construction areas like identity, billing, security, or layout.  |

Example of builder inheritance:

```python
EmployeeBuilder()
    .named("Alice")       # inherited from PersonBuilder
    .works_as("Engineer") # defined on EmployeeBuilder
```

Example of builder facets:

```python
CustomerAccountBuilder()
    .identity.named("Alice")
    .billing.with_card_token("tok_123")
    .security.enable_two_factor_auth()
```

Builder inheritance is about **specialized builders**.

Builder facets are about **organized builders**.

---

## 12. Builder inheritance and SOLID

### Single Responsibility Principle

Builder inheritance can improve SRP by letting each builder class focus on the construction steps for one level of the hierarchy.

```text
PersonBuilder -> person fields
EmployeeBuilder -> employee fields
```

### Open/Closed Principle

It can support OCP because you can add a new subclass builder without modifying the base builder.

```text
PersonBuilder
EmployeeBuilder
CustomerBuilder
ContractorBuilder
```

### Liskov Substitution Principle

This is the principle to be careful with.

If `EmployeeBuilder` inherits from `PersonBuilder`, then it should still behave like a valid `PersonBuilder`.

This can get tricky if subclass builders add stricter rules.

For example, `PersonBuilder.build()` may allow a person with just a name, but `EmployeeBuilder.build()` requires both name and position.

That may be acceptable if callers know they are using `EmployeeBuilder`, but it can be surprising if code expects any `PersonBuilder` to build after `.named(...)`.

So builder inheritance can introduce LSP concerns if build behavior changes too much.

---

## 13. Practical rule of thumb

Use builder inheritance when this sentence is true:

> The thing I am building inherits from another thing, and I want the child builder to reuse the parent builder’s fluent steps.

Avoid it when this sentence is true:

> I am using inheritance just to share builder methods.

If you only want method reuse, composition or helper classes may be cleaner.

---

## 14. Final summary

Builder inheritance lets subclass builders reuse parent builder steps while adding subclass-specific steps.

It is useful when:

* the final objects have a real inheritance relationship
* builders would otherwise duplicate common setup methods
* fluent chaining should continue after inherited builder methods

But it can become problematic when:

* the builder hierarchy gets too deep
* inheritance is used only for convenience
* subclass builders break expectations from parent builders

In one sentence:

> Builder inheritance is useful when your built objects form an inheritance hierarchy, and you want the builders to mirror that hierarchy while preserving fluent chaining.

---

[Exercise 3](exercise3.md)
