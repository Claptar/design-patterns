---
layout: default
title: "Builder Facets: Root-Builder Inheritance Approach"
---

# Builder Facets: Root-Builder Inheritance Approach

## 1. What this note explains

In the main Builder Facets notes, the implementation uses a separate shared base class called something like `BuilderFacet`.

That structure looks like this:

```text
CustomerAccountBuilder      -> root/facade builder
BuilderFacet                -> shared base for facets
IdentityBuilder             -> identity facet
BillingBuilder              -> billing facet
SecurityBuilder             -> security facet
NotificationBuilder         -> notification facet
```

There is another compact approach:

```text
CustomerAccountBuilder      -> root/facade builder
IdentityBuilder             -> inherits from CustomerAccountBuilder
BillingBuilder              -> inherits from CustomerAccountBuilder
SecurityBuilder             -> inherits from CustomerAccountBuilder
NotificationBuilder         -> inherits from CustomerAccountBuilder
```

In this version, each facet inherits from the root builder. That way, each facet automatically gets access to the root builder's navigation properties, such as `.identity`, `.billing`, `.security`, `.notifications`, and `.build()`.

This note explains that approach, shows how it works using the `CustomerAccountBuilder` example, and then discusses its tradeoffs.

---

## 2. The target fluent API

We still want the same public API:

```python
account = (
    CustomerAccountBuilder()
    .identity
        .named("Alice")
        .with_email("ALICE@EXAMPLE.COM")
    .billing
        .with_card_token("tok_123")
    .security
        .enable_two_factor_auth()
    .notifications
        .enable_sms_notifications()
    .build()
)
```

The construction still reads in terms of the account's configuration areas:

```text
identity
billing
security
notifications
```

The difference is internal implementation.

Instead of this:

```python
class IdentityBuilder(BuilderFacet):
    ...
```

we use this:

```python
class IdentityBuilder(CustomerAccountBuilder):
    ...
```

That means each facet is also treated as a kind of root builder.

---

## 3. Final object

The final object is the same as in the main Builder Facets notes.

```python
from dataclasses import dataclass


@dataclass
class CustomerAccount:
    name: str | None = None
    email: str | None = None
    card_token: str | None = None
    two_factor_auth: bool = False
    sms_notifications: bool = False
```

This object only stores the completed data.

The builders are responsible for constructing and validating it.

---

## 4. Root builder as facade

The root builder owns the `CustomerAccount` instance and exposes each facet.

```python
class CustomerAccountBuilder:
    def __init__(self, account=None):
        if account is None:
            self._account = CustomerAccount()
        else:
            self._account = account

    @property
    def identity(self):
        return IdentityBuilder(self._account)

    @property
    def billing(self):
        return BillingBuilder(self._account)

    @property
    def security(self):
        return SecurityBuilder(self._account)

    @property
    def notifications(self):
        return NotificationBuilder(self._account)

    def build(self):
        if not self._account.name:
            raise ValueError("Name is required")

        if not self._account.email:
            raise ValueError("Email is required")

        if self._account.sms_notifications and not self._account.two_factor_auth:
            raise ValueError("SMS notifications require two-factor authentication")

        return self._account
```

The constructor has two modes:

```python
CustomerAccountBuilder()
```

creates a new account.

```python
CustomerAccountBuilder(existing_account)
```

wraps an account that is already being built.

This two-mode constructor is what lets the root builder and the facet builders share the same account object.

---

## 5. Identity facet

The identity facet inherits from `CustomerAccountBuilder`.

```python
class IdentityBuilder(CustomerAccountBuilder):
    def __init__(self, account):
        super().__init__(account)

    def named(self, name):
        if not name.strip():
            raise ValueError("Name cannot be blank")

        self._account.name = name.strip()
        return self

    def with_email(self, email):
        email = email.strip().lower()

        if "@" not in email:
            raise ValueError("Invalid email address")

        self._account.email = email
        return self
```

Because `IdentityBuilder` inherits from `CustomerAccountBuilder`, it also has access to:

```text
.billing
.security
.notifications
.build()
```

So this works:

```python
CustomerAccountBuilder().identity.named("Alice").billing.with_card_token("tok_123")
```

After `.named("Alice")`, the chain is still on an `IdentityBuilder`. Since `IdentityBuilder` inherits `.billing`, the chain can jump to the billing facet.

---

## 6. Billing facet

```python
class BillingBuilder(CustomerAccountBuilder):
    def __init__(self, account):
        super().__init__(account)

    def with_card_token(self, card_token):
        if not card_token.startswith("tok_"):
            raise ValueError("Card token must start with 'tok_'")

        self._account.card_token = card_token
        return self
```

This facet owns billing-specific construction rules.

Since it inherits from `CustomerAccountBuilder`, it can also move to the other facets:

```python
CustomerAccountBuilder().billing.with_card_token("tok_123").security.enable_two_factor_auth()
```

---

## 7. Security facet

```python
class SecurityBuilder(CustomerAccountBuilder):
    def __init__(self, account):
        super().__init__(account)

    def enable_two_factor_auth(self):
        self._account.two_factor_auth = True
        return self
```

---

## 8. Notification facet

```python
class NotificationBuilder(CustomerAccountBuilder):
    def __init__(self, account):
        super().__init__(account)

    def enable_sms_notifications(self):
        self._account.sms_notifications = True
        return self
```

---

## 9. Full minimal example

```python
from dataclasses import dataclass


@dataclass
class CustomerAccount:
    name: str | None = None
    email: str | None = None
    card_token: str | None = None
    two_factor_auth: bool = False
    sms_notifications: bool = False


class CustomerAccountBuilder:
    def __init__(self, account=None):
        if account is None:
            self._account = CustomerAccount()
        else:
            self._account = account

    @property
    def identity(self):
        return IdentityBuilder(self._account)

    @property
    def billing(self):
        return BillingBuilder(self._account)

    @property
    def security(self):
        return SecurityBuilder(self._account)

    @property
    def notifications(self):
        return NotificationBuilder(self._account)

    def build(self):
        if not self._account.name:
            raise ValueError("Name is required")

        if not self._account.email:
            raise ValueError("Email is required")

        if self._account.sms_notifications and not self._account.two_factor_auth:
            raise ValueError("SMS notifications require two-factor authentication")

        return self._account


class IdentityBuilder(CustomerAccountBuilder):
    def __init__(self, account):
        super().__init__(account)

    def named(self, name):
        if not name.strip():
            raise ValueError("Name cannot be blank")

        self._account.name = name.strip()
        return self

    def with_email(self, email):
        email = email.strip().lower()

        if "@" not in email:
            raise ValueError("Invalid email address")

        self._account.email = email
        return self


class BillingBuilder(CustomerAccountBuilder):
    def __init__(self, account):
        super().__init__(account)

    def with_card_token(self, card_token):
        if not card_token.startswith("tok_"):
            raise ValueError("Card token must start with 'tok_'")

        self._account.card_token = card_token
        return self


class SecurityBuilder(CustomerAccountBuilder):
    def __init__(self, account):
        super().__init__(account)

    def enable_two_factor_auth(self):
        self._account.two_factor_auth = True
        return self


class NotificationBuilder(CustomerAccountBuilder):
    def __init__(self, account):
        super().__init__(account)

    def enable_sms_notifications(self):
        self._account.sms_notifications = True
        return self


account = (
    CustomerAccountBuilder()
    .identity
        .named("Alice")
        .with_email("ALICE@EXAMPLE.COM")
    .billing
        .with_card_token("tok_123")
    .security
        .enable_two_factor_auth()
    .notifications
        .enable_sms_notifications()
    .build()
)

print(account)
```

---

## 10. Why this approach works

The chain works because every facet is also a `CustomerAccountBuilder`.

For example:

```python
CustomerAccountBuilder().identity
```

returns an `IdentityBuilder`.

Then:

```python
.named("Alice")
```

returns that same `IdentityBuilder`.

Because `IdentityBuilder` inherits from `CustomerAccountBuilder`, this is available:

```python
.billing
```

which returns a `BillingBuilder` wrapping the same account object.

So the movement is:

```text
CustomerAccountBuilder
  .identity         -> IdentityBuilder(account)
  .named(...)      -> same IdentityBuilder
  .billing         -> BillingBuilder(same account)
  .with_card_token -> same BillingBuilder
  .security        -> SecurityBuilder(same account)
  .build()         -> validates and returns account
```

The trick is not that the builder objects are the same object. They are often different builder objects. The important part is that they all share the same `CustomerAccount` instance.

---

## 11. Strengths of this approach

### It is compact

There is no separate `BuilderFacet` class.

The root builder doubles as the shared base class for all facets.

### It gives a nice fluent API

You can write:

```python
CustomerAccountBuilder().identity.named("Alice").billing.with_card_token("tok_123").build()
```

without extra navigation methods.

### It is easy to understand in small examples

For simple examples, this approach can be easier to write and explain quickly.

The reader only needs to understand:

```text
facets inherit from the root builder
all builders share the same object being built
```

### It avoids duplicating navigation properties

Since the facet builders inherit from `CustomerAccountBuilder`, they automatically get:

```text
.identity
.billing
.security
.notifications
.build()
```

That is what enables cross-facet chaining.

---

## 12. Downsides of this approach

### 1. Facets are pretending to be the root builder

This is the main design downside.

```python
class IdentityBuilder(CustomerAccountBuilder):
    ...
```

This says:

> An `IdentityBuilder` is a kind of `CustomerAccountBuilder`.

Conceptually, that is not quite true.

An identity builder is not really the full root builder. It is a facet that configures identity-related fields.

Inheritance is being used here mostly to reuse `.billing`, `.security`, `.notifications`, and `.build()`.

That is convenient, but less precise than saying:

```python
class IdentityBuilder(BuilderFacet):
    ...
```

### 2. The root builder has two roles

The root builder constructor must support both:

```text
creating a new CustomerAccount
wrapping an existing CustomerAccount
```

That is why it takes an optional `account` parameter:

```python
def __init__(self, account=None):
    if account is None:
        self._account = CustomerAccount()
    else:
        self._account = account
```

This is practical, but it means `CustomerAccountBuilder` is serving two roles:

```text
root builder/facade
base class for facets
```

A separate facet base keeps those roles apart.

### 3. Every facet gets all root-builder behavior

Because facets inherit from the root builder, every facet automatically receives every root method and property.

That can be fine when the root builder is small.

But if the root builder later grows methods like this:

```python
def reset(self):
    ...

def clone(self):
    ...

def from_template(self, template):
    ...
```

then every facet gets those methods too.

Do you want `IdentityBuilder.reset()` or `BillingBuilder.from_template()` to exist?

Maybe not.

A separate `BuilderFacet` can expose only the behavior facets actually need.

### 4. Accessing a facet creates a new builder object each time

In this approach:

```python
@property
def identity(self):
    return IdentityBuilder(self._account)
```

Every access creates a new builder object.

This is usually not a performance problem because these objects are small.

But it matters if facet builders later hold their own state.

For example:

```python
class IdentityBuilder(CustomerAccountBuilder):
    def __init__(self, account):
        super().__init__(account)
        self._warnings = []
```

Now this is surprising:

```python
builder.identity
builder.identity
```

Those are two different `IdentityBuilder` instances, each with its own `_warnings` list.

The shared `BuilderFacet` approach often creates stable facet instances once:

```python
self._identity_builder = IdentityBuilder(self, self._account)
```

and then returns the same one each time.

### 5. The type hierarchy is less honest

This approach says:

```text
IdentityBuilder is a CustomerAccountBuilder
BillingBuilder is a CustomerAccountBuilder
SecurityBuilder is a CustomerAccountBuilder
```

But the more honest model is:

```text
CustomerAccountBuilder is the root builder
IdentityBuilder is a facet of CustomerAccountBuilder
BillingBuilder is a facet of CustomerAccountBuilder
SecurityBuilder is a facet of CustomerAccountBuilder
```

This distinction matters more as the codebase grows.

### 6. It can make type hints and IDE help a little muddy

At runtime, Python is fine with this style.

But with type hints, this design can be conceptually awkward because the facet classes inherit the root builder API even though they are not actually root builders.

A separate base like `BuilderFacet` makes the intent clearer to readers and tools:

```python
class IdentityBuilder(BuilderFacet):
    ...
```

That says exactly what the class is.

---

## 13. Is this approach bad?

No.

It is a valid approach, especially for small faceted builders.

It is compact and produces a pleasant fluent API.

It is a good fit when:

```text
the builder is small
there are only a few facets
facets do not hold their own state
the root builder has very little root-only behavior
the team prefers compactness over stricter role separation
```

It becomes less attractive when:

```text
there are many facets
facet builders hold local state
the root builder has root-only operations
clear type relationships matter
the code is part of a larger library or framework
```

---

## 14. Comparison with the separate `BuilderFacet` approach

| Question | Facets inherit root builder | Separate `BuilderFacet` base |
|---|---|---|
| Boilerplate | Less | More |
| Public fluent API | Good | Good |
| Role clarity | Weaker | Stronger |
| Type hierarchy | Less precise | More precise |
| Facet object stability | Usually new facet per access | Usually stable facet instances |
| Best for | Small examples and simple builders | Larger builders and teaching clarity |
| Main risk | Facets pretend to be root builders | Slightly more code |

Both approaches can produce the same public API.

The difference is mostly about internal structure and how well it scales.

---

## 15. Practical recommendation

Use the root-builder inheritance approach when you want a compact implementation and the builder is small.

Use a separate `BuilderFacet` base when you want clearer roles, stable facet objects, and a design that scales better as the builder grows.

In one sentence:

> Having facets inherit from the root builder is a compact way to get fluent cross-facet chaining, but it trades some conceptual clarity for convenience.

---

[Back to Builder Facets](builder_facets.md) · [Exercise 2](exercise2.md)
