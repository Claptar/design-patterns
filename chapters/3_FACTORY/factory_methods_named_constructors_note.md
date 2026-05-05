---
layout: default
title: Factory Methods as Named Constructors
---

# Factory Methods as Named Constructors

## 1. What problem are we trying to solve?

Sometimes a constructor is perfectly clear.

```python
user = User(name="Alice", email="alice@example.com")
point = Point(x=10, y=20)
```

There is no real ambiguity here. The caller can understand what is being created and what the arguments mean.

But sometimes a class has more than one natural way to create the same kind of object.

For example, imagine a `Money` class.

Internally, we may want to store money in cents:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount_in_cents: int
    currency: str
```

So we can create a value like this:

```python
price = Money(1299, "USD")
```

This works, but it is not very expressive.

What does `1299` mean?

```text
1299 dollars?
1299 cents?
1299 minor currency units?
```

The constructor call is valid, but the call site is not very clear.

A factory method can give that construction path a name.

```python
price = Money.from_dollars(12.99, "USD")
```

Now the meaning is obvious.

The method name explains how the object is being created.

---

## 2. Factory method as a named constructor

A **factory method** is a method that creates and returns an object.

In this note, we are focusing on one specific use of factory methods:

> A factory method can act as a named constructor.

That means its main job is not necessarily to choose between many different classes. Its job is to make object creation clearer.

Instead of this:

```python
price = Money(1299, "USD")
```

we can write this:

```python
price = Money.from_cents(1299, "USD")
```

Instead of this:

```python
price = Money(12.99, "USD")
```

which may not even match the internal representation, we can write this:

```python
price = Money.from_dollars(12.99, "USD")
```

The factory method gives a name to the conversion or interpretation being performed.

In plain English:

> Use a factory method when the method name makes object creation clearer than a direct constructor call.

---

## 3. Money example

Here is a simple version:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount_in_cents: int
    currency: str

    @classmethod
    def from_cents(cls, cents: int, currency: str):
        return cls(
            amount_in_cents=cents,
            currency=currency.upper(),
        )

    @classmethod
    def from_dollars(cls, amount: float, currency: str):
        return cls(
            amount_in_cents=round(amount * 100),
            currency=currency.upper(),
        )
```

Usage:

```python
price = Money.from_dollars(12.99, "usd")
fee = Money.from_cents(250, "usd")
```

Now each call explains itself.

```python
Money.from_dollars(12.99, "usd")
```

means:

```text
Take a dollar amount, convert it into cents, normalize the currency, and return Money.
```

And:

```python
Money.from_cents(250, "usd")
```

means:

```text
The amount is already in cents. Normalize the currency and return Money.
```

The constructor still exists, but callers do not always have to use it directly.

---

## 4. Why not just use the constructor?

You could write:

```python
price = Money(1299, "USD")
```

For very small examples, that may be fine.

But the problem is that the constructor exposes the internal representation.

The class stores cents, so callers need to know to pass cents.

That makes this mistake easy:

```python
price = Money(12.99, "USD")
```

The code looks reasonable, but it creates a bad object because the class expects cents.

A named constructor avoids that confusion:

```python
price = Money.from_dollars(12.99, "USD")
```

The caller no longer needs to remember the internal representation.

The method name tells them what kind of input is expected.

So the constructor says:

```text
Create Money from its internal representation.
```

The factory methods say:

```text
Create Money from this specific kind of input.
```

That is the useful distinction.

---

## 5. Another example: Point from Cartesian or polar coordinates

A `Point` gives us another natural example.

Imagine this constructor call:

```python
p = Point(2, 3)
```

What do the two numbers mean?

They could mean Cartesian coordinates:

```text
x = 2, y = 3
```

Or they could mean polar coordinates:

```text
rho = 2, theta = 3
```

Both are valid ways to describe a point, but they mean different things.

One possible solution is to add a coordinate-system argument:

```python
p = Point(2, 3, CoordinateSystem.POLAR)
```

That works, but now the constructor has generic parameter names like `a` and `b`, because those parameters mean different things depending on the coordinate system.

A clearer approach is to use named constructors:

```python
p1 = Point.from_cartesian(2, 3)
p2 = Point.from_polar(2, 3)
```

For example:

```python
from dataclasses import dataclass
from math import cos, sin


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    @classmethod
    def from_cartesian(cls, x: float, y: float):
        return cls(x=x, y=y)

    @classmethod
    def from_polar(cls, rho: float, theta: float):
        return cls(
            x=rho * cos(theta),
            y=rho * sin(theta),
        )
```

Usage:

```python
p1 = Point.from_cartesian(2, 3)
p2 = Point.from_polar(5, 0.927)
```

This is a good use of factory methods.

The class is still just `Point`. We are not creating separate `CartesianPoint` and `PolarPoint` classes. We are creating the same kind of object from two different input representations.

The factory method explains the interpretation of the arguments.

```python
Point.from_cartesian(2, 3)
```

means:

```text
Treat the inputs as x and y.
```

```python
Point.from_polar(5, 0.927)
```

means:

```text
Treat the inputs as rho and theta, then convert them to x and y.
```

That is exactly where named constructors are useful.

---

## 6. Real example from a popular Python library: pandas

A popular real-world example is `pandas.DataFrame`.

You can create a `DataFrame` directly:

```python
import pandas as pd


df = pd.DataFrame(data)
```

The `DataFrame` constructor is flexible. It can accept different shapes of input, such as dictionaries, arrays, iterables, and other DataFrames.

That flexibility is useful, but it can also make the call site less specific.

```python
df = pd.DataFrame(data)
```

This says:

```text
Build a DataFrame from some data.
```

But it does not say much about the shape of that data.

For clearer construction paths, pandas also provides class methods such as:

```python
df = pd.DataFrame.from_dict(data)
```

and:

```python
df = pd.DataFrame.from_records(records)
```

These are factory methods used as named constructors.

`from_dict` tells the reader:

```text
This input is dictionary-shaped.
Build the DataFrame by interpreting it as a dictionary.
```

`from_records` tells the reader:

```text
This input is record-shaped.
Each item probably represents one row.
Build the DataFrame from those records.
```

Compare this:

```python
df = pd.DataFrame(data)
```

with this:

```python
df = pd.DataFrame.from_records(records)
```

The second version communicates more intent.

That is the same design idea as:

```python
Money.from_dollars(12.99, "USD")
Point.from_polar(5, 0.927)
```

The factory method gives a name to the input interpretation.

---

## 7. When factory methods are worth using

Use a factory method when the constructor call does not clearly communicate the meaning of the input.

Good example:

```python
money = Money.from_dollars(12.99, "USD")
```

This is clearer than:

```python
money = Money(1299, "USD")
```

Use a factory method when the class has multiple natural creation paths.

```python
point = Point.from_cartesian(2, 3)
point = Point.from_polar(5, 0.927)
```

Both create a `Point`, but they interpret the inputs differently.

Use a factory method when creation involves conversion.

```python
money = Money.from_dollars(12.99, "USD")
```

The method converts dollars into cents before creating the object.

Use a factory method when creation involves normalization.

```python
money = Money.from_cents(250, "usd")
```

The method can normalize the currency to `"USD"`.

Use a factory method when the method name prevents mistakes.

```python
duration = Duration.from_seconds(90)
duration = Duration.from_minutes(1.5)
```

This is safer than:

```python
duration = Duration(90)
```

where the unit may not be obvious.

---

## 8. When factory methods are not worth using

Do not use a factory method when the constructor is already clear.

This is fine:

```python
point = Point(x=10, y=20)
```

This adds little value:

```python
point = Point.from_x_y(10, 20)
```

The method name does not add much because the constructor is already expressive.

Also avoid factory methods that merely repeat the constructor.

```python
class User:
    @classmethod
    def create(cls, name, email):
        return cls(name, email)
```

Usage:

```python
user = User.create("Alice", "alice@example.com")
```

If `create()` is not adding validation, conversion, normalization, or a clearer construction path, it is just extra ceremony.

Prefer:

```python
user = User("Alice", "alice@example.com")
```

Also avoid vague factory method names.

This is not very helpful:

```python
obj = Thing.create(data)
```

What kind of data?

What interpretation?

What is being created?

A better name explains the construction path:

```python
invoice = Invoice.from_json(data)
invoice = Invoice.from_csv_row(row)
invoice = Invoice.from_database_record(record)
```

The value of the method is in the name.

---

## 9. Static method or class method?

In Python, named constructors are usually written as `@classmethod`.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount_in_cents: int
    currency: str

    @classmethod
    def from_dollars(cls, amount: float, currency: str):
        return cls(
            amount_in_cents=round(amount * 100),
            currency=currency.upper(),
        )
```

The important part is `cls`.

```python
return cls(...)
```

means:

```text
Create an instance of this class.
```

A static method usually hardcodes the class:

```python
@dataclass(frozen=True)
class Money:
    amount_in_cents: int
    currency: str

    @staticmethod
    def from_dollars(amount: float, currency: str):
        return Money(
            amount_in_cents=round(amount * 100),
            currency=currency.upper(),
        )
```

This works, but it is less flexible.

For named constructors, prefer `@classmethod` unless you have a specific reason not to.

---

## 10. Practical rule of thumb

Ask:

> Does the constructor call clearly explain what the arguments mean?

If yes, use the constructor.

```python
user = User(name="Alice", email="alice@example.com")
```

Ask:

> Are there multiple natural ways to create this object?

If yes, factory methods may help.

```python
Point.from_cartesian(2, 3)
Point.from_polar(5, 0.927)
```

Ask:

> Does creation involve conversion, parsing, normalization, or interpretation?

If yes, a factory method can make that explicit.

```python
Money.from_dollars(12.99, "USD")
pd.DataFrame.from_records(records)
```

Ask:

> Am I only wrapping the constructor with a different name?

If yes, the factory method is probably unnecessary.

---

## 11. Final summary

Factory methods are useful when a class has more than one clear way to be created.

They are especially helpful when constructor arguments would otherwise be ambiguous.

A good factory method can:

- give a construction path a clear name
- explain the meaning of the input
- hide conversion details
- hide normalization details
- prevent callers from depending too much on internal representation
- make call sites easier to read

Do not use a factory method just to wrap a simple constructor.

In one sentence:

> Use a factory method when the method name makes object creation clearer than a direct constructor call.

---

[Factories](factory.md)

