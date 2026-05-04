---
layout: default
title: Builder Design Pattern
---

# Builder Design Pattern

## 1. The core question

At first, Builder can look like a complicated way of collecting data before calling a constructor.

For simple objects, that criticism is correct.

```python
user = (
    UserBuilder()
    .with_name("Alice")
    .with_email("alice@example.com")
    .build()
)
```

If the alternative is just this:

```python
user = User(name="Alice", email="alice@example.com")
```

then the builder is probably unnecessary.

The Builder pattern becomes useful when **object construction is a process**, not just assigning a few fields.

A good Builder can handle:

* required fields
* optional fields
* defaults
* validation
* normalization
* derived values
* invalid combinations
* step-by-step assembly
* immutable final objects
* hiding messy construction details

So a better mental model is:

> Builder is not just a fancy constructor. It is an object that owns the construction process for another object.

---

## 2. The problem Builder solves

Imagine a class that represents an HTTP request:

```python
class HttpRequest:
    def __init__(
        self,
        method,
        url,
        headers,
        query_params,
        json_body,
        timeout_seconds,
        retry_count,
    ):
        self.method = method
        self.url = url
        self.headers = headers
        self.query_params = query_params
        self.json_body = json_body
        self.timeout_seconds = timeout_seconds
        self.retry_count = retry_count
```

A request might be created like this:

```python
request = HttpRequest(
    "POST",
    "https://api.billing.com/customers/123/invoices",
    {
        "Authorization": "Bearer abc123",
        "Content-Type": "application/json",
        "Idempotency-Key": "invoice-789",
    },
    {
        "expand": "payments",
    },
    {
        "amount": 4900,
        "currency": "usd",
        "description": "Monthly subscription",
    },
    10,
    3,
)
```

This is hard to read, but readability is only part of the problem.

The deeper problem is that request construction has rules.

For example:

* `GET` requests should not have JSON bodies.
* `POST` requests with JSON bodies need `Content-Type: application/json`.
* Authenticated requests need an `Authorization` header.
* Idempotency keys should only be used for unsafe methods like `POST`, `PATCH`, and `DELETE`.
* Timeout must be positive.
* Retry count cannot be negative.
* Query parameters should be converted to strings.
* The final request object should not be partially valid.

If those rules are scattered across the codebase, every caller must remember them. That is fragile.

If all those rules go into the `HttpRequest` constructor, the constructor becomes complicated.

Builder gives those construction rules a dedicated home.

---

## 3. Builder example: HTTP request builder

First, keep the final object simple.

```python
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HttpRequest:
    method: str
    url: str
    headers: dict[str, str]
    query_params: dict[str, str]
    json_body: dict[str, Any] | None
    timeout_seconds: int
    retry_count: int
```

The final object just represents a valid request. It does not need to know every detail of how to build one.

Now create a builder:

```python
class HttpRequestBuilder:
    def __init__(self):
        self._method = None
        self._url = None
        self._headers = {}
        self._query_params = {}
        self._json_body = None
        self._timeout_seconds = 10
        self._retry_count = 0
        self._auth_token = None
        self._idempotency_key = None

    def get(self, url):
        self._method = "GET"
        self._url = url
        return self

    def post(self, url):
        self._method = "POST"
        self._url = url
        return self

    def with_auth_token(self, token):
        self._auth_token = token
        return self

    def with_header(self, name, value):
        self._headers[name] = value
        return self

    def with_query_param(self, name, value):
        self._query_params[name] = str(value)
        return self

    def with_json_body(self, body):
        self._json_body = body
        return self

    def with_idempotency_key(self, key):
        self._idempotency_key = key
        return self

    def with_timeout(self, seconds):
        self._timeout_seconds = seconds
        return self

    def with_retries(self, count):
        self._retry_count = count
        return self

    def build(self):
        if not self._method:
            raise ValueError("HTTP method is required")

        if not self._url:
            raise ValueError("URL is required")

        if self._timeout_seconds <= 0:
            raise ValueError("Timeout must be positive")

        if self._retry_count < 0:
            raise ValueError("Retry count cannot be negative")

        if self._method == "GET" and self._json_body is not None:
            raise ValueError("GET requests cannot have a JSON body")

        headers = dict(self._headers)

        if self._auth_token:
            headers["Authorization"] = f"Bearer {self._auth_token}"

        if self._json_body is not None:
            headers["Content-Type"] = "application/json"

        if self._idempotency_key:
            if self._method not in {"POST", "PATCH", "DELETE"}:
                raise ValueError("Idempotency keys only apply to unsafe methods")

            headers["Idempotency-Key"] = self._idempotency_key

        return HttpRequest(
            method=self._method,
            url=self._url,
            headers=headers,
            query_params=dict(self._query_params),
            json_body=self._json_body,
            timeout_seconds=self._timeout_seconds,
            retry_count=self._retry_count,
        )
```

Usage:

```python
request = (
    HttpRequestBuilder()
    .post("https://api.billing.com/customers/123/invoices")
    .with_auth_token("abc123")
    .with_query_param("expand", "payments")
    .with_json_body({
        "amount": 4900,
        "currency": "usd",
        "description": "Monthly subscription",
    })
    .with_idempotency_key("invoice-789")
    .with_timeout(10)
    .with_retries(3)
    .build()
)
```

Now the builder is doing useful work:

* setting defaults
* validating invalid combinations
* deriving headers
* normalizing query parameters
* protecting the final object from invalid state
* making the construction readable
* centralizing construction rules

This is much more than just collecting constructor arguments.

---

## 4. Why not just put this in `HttpRequest.__init__`?

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

## 5. Invalid construction example

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

## 6. Another natural example: SQL query builder

Another place where Builder feels natural is query construction.

A query has optional parts:

* selected columns
* table
* filters
* parameters
* sorting
* limit

It also has rules:

* `SELECT` must have columns.
* `FROM` must have a table.
* `WHERE` clauses should be parameterized.
* `LIMIT` must be positive.
* Sort direction should be controlled.
* The final SQL string should be assembled consistently.

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

## 7. Builder versus constructor

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

## 8. Builder versus factory

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

## 9. Builder and SOLID

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

## 10. When Builder is worth using

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

## 11. When Builder is too much

Do not use Builder when:

* the object has only two or three obvious fields
* there are no optional combinations
* there is no validation or normalization
* construction is already readable
* the builder just repeats the constructor

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

## 12. Practical rule of thumb

Ask:

> Is object creation becoming a meaningful process with rules, defaults, validation, or assembly steps?

If yes, Builder may help.

Ask:

> Am I just wrapping a normal constructor with extra method calls?

If yes, Builder is probably overengineering.

---

## 13. Final summary

The Builder pattern is useful when creating an object is not just assigning fields, but following a construction process.

A strong Builder can:

* collect required and optional inputs
* apply defaults
* validate inputs
* reject invalid combinations
* normalize values
* derive extra fields
* hide messy assembly details
* produce a clean, valid, often immutable final object

In one sentence:

> Builder is worth using when construction has enough rules or steps that you want a dedicated object to manage the process before producing the final object.
