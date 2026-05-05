---
layout: default
title: Gamma Categorization of Design Patterns
---

# Gamma Categorization of Design Patterns

**Gamma categorization** is a way of grouping the classic **Gang of Four design patterns** into three categories:

```text
Creational
Structural
Behavioral
```

It is named after **Erich Gamma**, one of the four authors of *Design Patterns: Elements of Reusable Object-Oriented Software*. The book catalogued 23 classic object-oriented design patterns, commonly known as the **Gang of Four** or **GoF** patterns.

---

## 1. Creational Patterns

**Creational patterns are about object creation.**

They help answer:

> “How should objects be created without tightly coupling my code to specific classes?”

Use them when object creation is becoming messy, repetitive, conditional, or needs to be hidden behind an abstraction.

### Common creational patterns

| Pattern | Main idea |
|---|---|
| Factory Method | Let subclasses or factory methods decide which object to create. |
| Abstract Factory | Create families of related objects. |
| Builder | Construct complex objects step by step. |
| Prototype | Clone existing objects. |
| Singleton | Ensure only one instance exists. |

### Example problem

```python
if notification_type == "email":
    sender = EmailSender()
elif notification_type == "sms":
    sender = SmsSender()
elif notification_type == "push":
    sender = PushSender()
```

This code spreads object-creation decisions into the main business logic.

A creational pattern, such as a factory, can move that logic elsewhere:

```python
sender = sender_factory.create(notification_type)
sender.send(message)
```

The goal is to avoid hard-coding object creation throughout the codebase.

---

## 2. Structural Patterns

**Structural patterns are about how classes and objects are composed.**

They help answer:

> “How do I connect objects together cleanly?”

Use them when you need to wrap, adapt, combine, simplify, or protect access to objects.

### Common structural patterns

| Pattern | Main idea |
|---|---|
| Adapter | Make one interface work like another. |
| Decorator | Add behavior without changing the original object. |
| Facade | Provide a simpler interface over a complex subsystem. |
| Composite | Treat individual objects and groups uniformly. |
| Proxy | Control access to another object. |
| Bridge | Separate abstraction from implementation. |
| Flyweight | Share objects to reduce memory use. |

### Example problem

Your app expects this:

```python
payment_processor.charge(amount)
```

But a third-party API gives you this:

```python
stripe_client.create_payment_intent(...)
```

An **Adapter** can translate between them:

```python
class StripePaymentAdapter:
    def __init__(self, stripe_client):
        self.stripe_client = stripe_client

    def charge(self, amount):
        return self.stripe_client.create_payment_intent(amount)
```

The goal is to make object relationships cleaner and reduce awkward coupling.

---

## 3. Behavioral Patterns

**Behavioral patterns are about communication and responsibility between objects.**

They help answer:

> “Which object should do what, and how should objects interact?”

Use them when logic involves algorithms, workflows, state changes, notifications, commands, or coordination between objects.

### Common behavioral patterns

| Pattern | Main idea |
|---|---|
| Strategy | Swap algorithms or behaviors at runtime. |
| Observer | Notify many objects when something changes. |
| Command | Represent an action as an object. |
| State | Change behavior when internal state changes. |
| Template Method | Define an algorithm skeleton with customizable steps. |
| Chain of Responsibility | Pass a request through handlers. |
| Mediator | Coordinate communication through a central object. |
| Iterator | Traverse a collection without exposing internals. |
| Visitor | Add operations to object structures. |
| Memento | Save and restore state. |

### Example problem

```python
if customer.is_nonprofit:
    amount *= 0.8

if customer.has_annual_contract:
    amount *= 0.9

if customer.coupon_code == "WELCOME10":
    amount *= 0.9
```

A **Strategy** or rule-based approach can separate discount behavior:

```python
for discount in discounts:
    amount = discount.apply(customer, amount)
```

The goal is to make behavior easier to change without turning one method into a giant pile of conditionals.

---

## Quick Mental Model

| Category | Concern | Question |
|---|---|---|
| Creational | Creating objects | “How do I create this cleanly?” |
| Structural | Combining objects | “How do I connect these cleanly?” |
| Behavioral | Coordinating behavior | “How should these objects interact?” |

---

## House Analogy

Think of building a house:

```text
Creational: How do we create the parts?
Structural: How do we assemble the parts?
Behavioral: How do the parts work together?
```

---

## Connection to SOLID

Gamma categorization and SOLID are related, but they are not the same thing.

**SOLID** gives design principles:

```text
Keep responsibilities focused.
Depend on abstractions.
Avoid rigid inheritance.
Keep interfaces small.
Make code extensible.
```

**Gamma categorization** organizes reusable design patterns:

```text
Creational patterns solve object creation problems.
Structural patterns solve object composition problems.
Behavioral patterns solve object interaction problems.
```

So when you look at messy code, you might first diagnose it with SOLID, then choose a pattern category.

Examples:

| Smell | Possible pattern category |
|---|---|
| Too many `new SomeClass()` calls | Creational |
| Objects do not fit together cleanly | Structural |
| Too many conditionals controlling behavior | Behavioral |

---

## One-Sentence Summary

Gamma categorization groups design patterns by what kind of design problem they solve:

> Creating objects, composing objects, or coordinating behavior.

---

[Home](../../index.md)
