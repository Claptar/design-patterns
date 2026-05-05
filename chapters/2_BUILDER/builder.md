---
layout: default
title: Builder Design Pattern
---

# Builder Design Pattern

## 1. What problem are we trying to solve?

Some objects are easy to create.

```python
user = User(name="Alice", email="alice@example.com")
point = Point(x=10, y=20)
```

There is no need for a design pattern here. The constructor is clear, the inputs are obvious, and there are not many rules involved.

But some objects are harder to create correctly. They may have many optional settings, sensible defaults, validation rules, derived values, or combinations of inputs that should not be allowed.

For example, imagine building an HTTP request. A request may need:

- a method, such as `GET` or `POST`
- a URL
- headers
- query parameters
- authentication
- a JSON body
- timeout settings
- retry settings
- an idempotency key

The issue is not only that there are many fields. The deeper issue is that these fields have rules.

For example:

- `GET` requests should not have JSON bodies.
- Requests with JSON bodies should have a `Content-Type: application/json` header.
- Authenticated requests need an `Authorization` header.
- Idempotency keys should only be used with unsafe methods like `POST`, `PATCH`, and `DELETE`.
- Timeout values should be positive.
- Retry counts should not be negative.

When construction has this kind of logic, a plain constructor call can become hard to read and easy to misuse.

That is the kind of problem the **Builder pattern** is meant to solve.

---

## 2. Builder

A **builder** is an object whose job is to construct another object step by step.

Instead of passing every value into one constructor call, you give the builder a sequence of construction instructions. When the builder has enough information, you call `build()` and it creates the final object.

In many examples, builder methods return `self`. That allows a fluent style:

```python
thing = (
    ThingBuilder()
    .set_one_value(...)
    .set_another_value(...)
    .build()
)
```

The final object is often simple. The builder is where temporary construction state, defaults, and validation can live.

Here is a deliberately small toy example.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Sandwich:
    bread: str
    filling: str
    toasted: bool
    extras: tuple[str, ...]
```

A normal constructor call might look like this:

```python
sandwich = Sandwich(
    bread="sourdough",
    filling="cheese",
    toasted=True,
    extras=("tomato", "pickles"),
)
```

That is already readable. But we can still use it to show the shape of a builder.

```python
class SandwichBuilder:
    def __init__(self):
        self._bread = "white"
        self._filling = None
        self._toasted = False
        self._extras = []

    def on_bread(self, bread):
        self._bread = bread
        return self

    def with_filling(self, filling):
        self._filling = filling
        return self

    def toasted(self):
        self._toasted = True
        return self

    def add_extra(self, extra):
        self._extras.append(extra)
        return self

    def build(self):
        if not self._filling:
            raise ValueError("A sandwich needs a filling")

        return Sandwich(
            bread=self._bread,
            filling=self._filling,
            toasted=self._toasted,
            extras=tuple(self._extras),
        )
```

Usage:

```python
sandwich = (
    SandwichBuilder()
    .on_bread("sourdough")
    .with_filling("cheese")
    .toasted()
    .add_extra("tomato")
    .add_extra("pickles")
    .build()
)
```

The builder is doing a few simple things:

- keeping temporary state while the sandwich is being configured
- providing defaults, such as `"white"` bread
- exposing readable construction steps
- validating that the required filling exists
- creating the final immutable `Sandwich`

---

## 3. Why not just put this in `HttpRequest.__init__`?

You can put all the logic in the constructor, but then `HttpRequest` has two jobs:

1. represent a request
2. construct and validate a request

That can become messy.

A cleaner split is:

```text
HttpRequest        -> represents a completed valid request
HttpRequestBuilder -> knows how to construct a completed valid request
```

This is especially useful when the final object should be immutable.

```python
@dataclass(frozen=True)
class HttpRequest:
    ...
```

The builder can be mutable while construction is in progress. The final object can be immutable once built.

---

## 4. Invalid construction example

Without a builder, a caller might accidentally create a bad request:

```python
request = HttpRequest(
    method="GET",
    url="/customers",
    headers={"Idempotency-Key": "abc"},
    query_params={},
    json_body={"bad": "GET should not have this"},
    timeout_seconds=-5,
    retry_count=-2,
)
```

The object is invalid unless the constructor becomes very defensive.

With the builder:

```python
request = (
    HttpRequestBuilder()
    .get("/customers")
    .with_json_body({"bad": "GET should not have this"})
    .with_timeout(-5)
    .build()
)
```

`build()` can reject it before producing the final object.

Possible errors:

```text
GET requests cannot have a JSON body.
Timeout must be positive.
```

That is where Builder starts to earn its keep.

---

## 5. Another natural example: SQL query builder

Another place where Builder feels natural is query construction.

A query has optional parts:

- selected columns
- table
- filters
- parameters
- sorting
- limit

It also has rules:

- `SELECT` must have columns.
- `FROM` must have a table.
- `WHERE` clauses should be parameterized.
- `LIMIT` must be positive.
- Sort direction should be controlled.
- The final SQL string should be assembled consistently.

A builder can centralize that construction.

```python
class SelectQueryBuilder:
    def __init__(self):
        self._columns = []
        self._table = None
        self._where = []
        self._params = {}
        self._order_by = None
        self._limit = None

    def select(self, *columns):
        self._columns.extend(columns)
        return self

    def from_table(self, table):
        self._table = table
        return self

    def where(self, condition, **params):
        self._where.append(condition)
        self._params.update(params)
        return self

    def order_by(self, column, direction="ASC"):
        direction = direction.upper()

        if direction not in {"ASC", "DESC"}:
            raise ValueError("Sort direction must be ASC or DESC")

        self._order_by = f"{column} {direction}"
        return self

    def limit(self, count):
        if count <= 0:
            raise ValueError("Limit must be positive")

        self._limit = count
        return self

    def build(self):
        if not self._columns:
            raise ValueError("At least one selected column is required")

        if not self._table:
            raise ValueError("Table is required")

        sql = f"SELECT {', '.join(self._columns)} FROM {self._table}"

        if self._where:
            sql += " WHERE " + " AND ".join(self._where)

        if self._order_by:
            sql += f" ORDER BY {self._order_by}"

        if self._limit:
            sql += f" LIMIT {self._limit}"

        return sql, self._params
```

Usage:

```python
sql, params = (
    SelectQueryBuilder()
    .select("id", "total", "created_at")
    .from_table("orders")
    .where("customer_id = :customer_id", customer_id=123)
    .where("status = :status", status="paid")
    .order_by("created_at", "DESC")
    .limit(50)
    .build()
)
```

This is useful because the builder is not merely collecting fields. It is assembling a valid query while enforcing some construction rules.

---

## 6. Builder versus constructor

Use a normal constructor when construction is simple:

```python
point = Point(10, 20)
```

A builder would be overkill:

```python
point = (
    PointBuilder()
    .with_x(10)
    .with_y(20)
    .build()
)
```

The builder adds ceremony but not much value.

Use a builder when a constructor call becomes unclear or unsafe:

```python
request = HttpRequest(
    "POST",
    url,
    headers,
    query_params,
    body,
    10,
    3,
)
```

Especially when the object has validation rules or invalid combinations.

---

## 7. Builder versus factory

Builder and Factory are both creational patterns, but they solve different problems.

| Pattern | Main question                            | Example                                                                          |
| ------- | ---------------------------------------- | -------------------------------------------------------------------------------- |
| Factory | Which object should I create?            | Choose `StripePaymentProcessor` or `PayPalPaymentProcessor`.                     |
| Builder | How do I assemble this object correctly? | Build an HTTP request with method, auth, headers, body, timeout, and validation. |

Factory example:

```python
processor = PaymentProcessorFactory.create(customer.payment_provider)
```

The main decision is **which class** to instantiate.

Builder example:

```python
request = (
    HttpRequestBuilder()
    .post(url)
    .with_auth_token(token)
    .with_json_body(body)
    .with_timeout(10)
    .build()
)
```

The main challenge is **assembling one complex object correctly**.

They can also work together. A factory might choose the right builder, and the builder might construct the object.

---

## 8. Builder and SOLID

Builder often supports SOLID principles, especially Single Responsibility Principle.

| Principle                       | Connection                                                                                |
| ------------------------------- | ----------------------------------------------------------------------------------------- |
| Single Responsibility Principle | Construction logic moves out of the final object or calling code.                         |
| Open/Closed Principle           | New optional construction steps can sometimes be added without changing existing callers. |
| Dependency Inversion Principle  | Callers can depend on a builder abstraction if needed.                                    |
| Interface Segregation Principle | Different builders can expose only the construction steps relevant to their use case.     |
| Liskov Substitution Principle   | Different builders sharing a contract should produce compatible results.                  |

The strongest connection is usually SRP.

Instead of one class doing both:

```text
represent the final object
manage complex construction rules
```

Builder separates those responsibilities.

---

## 9. When Builder is worth using

Use Builder when object construction involves:

| Situation                 | Why Builder helps                                             |
| ------------------------- | ------------------------------------------------------------- |
| Many optional fields      | Avoids huge, unclear constructor calls.                       |
| Many valid combinations   | Avoids many overloaded constructors or factory methods.       |
| Defaults                  | Builder can set sensible defaults.                            |
| Validation                | `build()` can reject invalid state.                           |
| Normalization             | Builder can convert values before construction.               |
| Derived fields            | Builder can compute values like headers or file names.        |
| Invalid combinations      | Builder can reject combinations like GET request + JSON body. |
| Step-by-step construction | Builder can gather pieces gradually.                          |
| Immutable final object    | Builder stays mutable, final object stays frozen.             |

---

## 10. When Builder is too much

Do not use Builder when:

- the object has only two or three obvious fields
- there are no optional combinations
- there is no validation or normalization
- construction is already readable
- the builder just repeats the constructor

Bad builder example:

```python
class PointBuilder:
    def with_x(self, x):
        self.x = x
        return self

    def with_y(self, y):
        self.y = y
        return self

    def build(self):
        return Point(self.x, self.y)
```

This adds complexity without much benefit.

Prefer:

```python
point = Point(10, 20)
```

---

## 11. Practical rule of thumb

Ask:

> Is object creation becoming a meaningful process with rules, defaults, validation, or assembly steps?

If yes, Builder may help.

Ask:

> Am I just wrapping a normal constructor with extra method calls?

If yes, Builder is probably overengineering.

---

## 12. Final summary

The Builder pattern is useful when creating an object is not just assigning fields, but following a construction process.

A strong Builder can:

- collect required and optional inputs
- apply defaults
- validate inputs
- reject invalid combinations
- normalize values
- derive extra fields
- hide messy assembly details
- produce a clean, valid, often immutable final object

In one sentence:

> Builder is worth using when construction has enough rules or steps that you want a dedicated object to manage the process before producing the final object.

---

## Exercise

[Exercise 1: Notification Builder](exercise1.md)
