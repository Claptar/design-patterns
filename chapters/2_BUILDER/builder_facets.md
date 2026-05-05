---
layout: default
title: "Builder Facets: Fluent Faceted Builder Pattern"
---

# Builder Facets: Fluent Faceted Builder Pattern

## 1. What are builder facets?

**Builder facets** are a variation of the Builder pattern where one large builder is split into several smaller builders, each responsible for one area of the final object.

A regular builder solves this problem:

> This object has many construction steps.

A faceted builder solves this more specific problem:

> This object has many construction steps, and those steps naturally belong to different categories.

For example, a `CustomerAccount` might have several configuration areas:

```text
identity
billing
notifications
security
```

Instead of one huge builder with every method on it, we can create separate builder facets:

```text
CustomerAccountBuilder
├── identity
├── billing
├── notifications
└── security
```

Each facet works on the same final object.

---

## 2. Why facets help

A normal builder might become crowded:

```python
account = (
    CustomerAccountBuilder()
    .with_name("Alice")
    .with_email("alice@example.com")
    .with_billing_address("10 Main Street")
    .with_vat_number("GB123")
    .with_card_token("tok_123")
    .enable_email_notifications()
    .enable_sms_notifications()
    .enable_two_factor_auth()
    .enable_login_alerts()
    .build()
)
```

This is fluent, but the builder has become a dumping ground for unrelated construction concerns.

A faceted builder organizes the same construction process like this:

```python
account = (
    CustomerAccountBuilder()
    .identity
        .named("Alice")
        .with_email("ALICE@EXAMPLE.COM")
    .billing
        .with_billing_address("10 Main Street")
        .with_vat_number("gb123")
        .with_card_token("tok_123")
    .security
        .enable_two_factor_auth()
        .enable_login_alerts()
    .notifications
        .enable_email_notifications()
        .enable_sms_notifications()
    .build()
)
```

Now the chain shows which part of the account is being configured.

---

## 3. The API we want

Before looking at implementation, start with the desired usage.

We want code like this:

```python
account = (
    CustomerAccountBuilder()
    .identity
        .named("Alice")
        .with_email("alice@example.com")
    .billing
        .with_card_token("tok_123")
    .security
        .enable_two_factor_auth()
    .notifications
        .enable_sms_notifications()
    .build()
)
```

This should read as:

```text
Build a customer account.
Configure identity.
Configure billing.
Configure security.
Configure notifications.
Then validate and build the account.
```

The goal is not just shorter code. The goal is to make construction read in terms of the object's real configuration areas.

---

## 4. The implementation idea in one picture

The final object is shared.

The root builder owns it.

Each facet modifies one part of it.

```text
                  CustomerAccountBuilder
                           │
                           │ owns
                           ▼
                    CustomerAccount
                           ▲
        ┌──────────────────┼──────────────────┐
        │                  │                  │
 IdentityBuilder     BillingBuilder     SecurityBuilder
        │                  │                  │
        └──────── all modify the same account ┘
```

The root builder exposes facets:

```python
builder.identity
builder.billing
builder.notifications
builder.security
```

Each facet knows how to get back to the root builder so the chain can move from one facet to another.

---

## 5. Minimal working example

This section uses only a few fields so the mechanism is easy to see.

### Final object

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

The final object is intentionally simple. It only stores the completed data.

### Root builder

```python
class CustomerAccountBuilder:
    def __init__(self):
        self._account = CustomerAccount()
        self._identity_builder = IdentityBuilder(self, self._account)
        self._billing_builder = BillingBuilder(self, self._account)
        self._security_builder = SecurityBuilder(self, self._account)
        self._notifications_builder = NotificationBuilder(self, self._account)

    @property
    def identity(self):
        return self._identity_builder

    @property
    def billing(self):
        return self._billing_builder

    @property
    def security(self):
        return self._security_builder

    @property
    def notifications(self):
        return self._notifications_builder

    def build(self):
        if not self._account.name:
            raise ValueError("Name is required")

        if not self._account.email:
            raise ValueError("Email is required")

        if self._account.sms_notifications and not self._account.two_factor_auth:
            raise ValueError("SMS notifications require two-factor authentication")

        return self._account
```

The root builder has two jobs:

1. own the object being built,
2. validate rules that involve multiple facets.

The private fields use names like `_identity_builder` because they store builder facet objects, not identity data. The public property remains `.identity` so the fluent API reads naturally.


For example, this rule involves both notifications and security:

```text
SMS notifications require two-factor authentication.
```

So it belongs in the root builder.

### Shared facet base

To move fluently between facets, each facet needs access to the root builder.

```python
class BuilderFacet:
    def __init__(self, root, account):
        self._root = root
        self._account = account

    @property
    def identity(self):
        return self._root.identity

    @property
    def billing(self):
        return self._root.billing

    @property
    def security(self):
        return self._root.security

    @property
    def notifications(self):
        return self._root.notifications

    def build(self):
        return self._root.build()
```

This is the small trick that allows cross-facet chaining.

A method like `.named(...)` returns the current facet.

A property like `.billing` returns another facet.

A method like `.build()` delegates back to the root builder.

### Identity facet

```python
class IdentityBuilder(BuilderFacet):
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

Identity-specific input rules stay in the identity facet.

### Billing facet

```python
class BillingBuilder(BuilderFacet):
    def with_card_token(self, card_token):
        if not card_token.startswith("tok_"):
            raise ValueError("Card token must start with 'tok_'")

        self._account.card_token = card_token
        return self
```

Billing-specific input rules stay in the billing facet.

### Security facet

```python
class SecurityBuilder(BuilderFacet):
    def enable_two_factor_auth(self):
        self._account.two_factor_auth = True
        return self
```

### Notification facet

```python
class NotificationBuilder(BuilderFacet):
    def enable_sms_notifications(self):
        self._account.sms_notifications = True
        return self
```

### Usage

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

This is the minimal version of the pattern.

---

## 6. How fluent chaining actually works

The chain works because there are three kinds of operations.

### 1. Methods inside a facet return `self`

```python
def named(self, name):
    self._account.name = name
    return self
```

So this stays inside the identity facet:

```python
.identity.named("Alice").with_email("alice@example.com")
```

### 2. Facet navigation properties return another facet

```python
@property
def billing(self):
    return self._root.billing
```

So after working in identity, this can jump to billing:

```python
.identity.named("Alice").billing.with_card_token("tok_123")
```

### 3. `build()` delegates to the root builder

```python
def build(self):
    return self._root.build()
```

So you can call `.build()` from whichever facet you are currently in.

The full movement looks like this:

```text
.identity
    returns IdentityBuilder

.named(...)
    returns IdentityBuilder

.billing
    returns BillingBuilder

.with_card_token(...)
    returns BillingBuilder

.security
    returns SecurityBuilder

.build()
    calls CustomerAccountBuilder.build()
```

That is the core fluent-facet mechanism.

---

## 7. Where validation belongs

Builder facets are useful because validation can be split naturally.

### Local validation

Local validation belongs inside the facet that owns that area.

Example:

```python
class BillingBuilder(BuilderFacet):
    def with_card_token(self, card_token):
        if not card_token.startswith("tok_"):
            raise ValueError("Card token must start with 'tok_'")

        self._account.card_token = card_token
        return self
```

This rule is purely about billing, so it belongs in `BillingBuilder`.

### Global validation

Global validation belongs in the root builder.

Example:

```python
class CustomerAccountBuilder:
    def build(self):
        if self._account.sms_notifications and not self._account.two_factor_auth:
            raise ValueError("SMS notifications require two-factor authentication")

        return self._account
```

This rule involves two facets:

```text
notifications
security
```

So it belongs in the root builder.

A good rule of thumb:

```text
If the rule only mentions one facet, put it in that facet.
If the rule connects multiple facets, put it in the root builder.
```

---

## 8. Complete example with more fields

The minimal example above showed the mechanism. A fuller account builder might include more fields:

```python
from dataclasses import dataclass


@dataclass
class CustomerAccount:
    name: str | None = None
    email: str | None = None

    billing_address: str | None = None
    vat_number: str | None = None
    card_token: str | None = None

    email_notifications: bool = False
    sms_notifications: bool = False

    two_factor_auth: bool = False
    login_alerts: bool = False
```

The same structure still applies:

```text
CustomerAccountBuilder
  identity      -> name, email
  billing       -> address, VAT number, card token
  notifications -> email notifications, SMS notifications
  security      -> two-factor auth, login alerts
```

The fuller usage might look like this:

```python
account = (
    CustomerAccountBuilder()
    .identity
        .named("Alice")
        .with_email("ALICE@EXAMPLE.COM")
    .billing
        .with_billing_address("10 Main Street")
        .with_vat_number("gb123")
        .with_card_token("tok_123")
    .security
        .enable_two_factor_auth()
        .enable_login_alerts()
    .notifications
        .enable_email_notifications()
        .enable_sms_notifications()
    .build()
)
```

At this size, facets start to feel more useful. The construction process has several clear areas, and grouping them improves readability.

---

## 9. Another place facets appear: HTTP request builders

A faceted HTTP request builder could have these facets:

```text
route
auth
headers
body
reliability
```

Usage might look like this:

```python
request = (
    HttpRequestBuilder()
    .route
        .post("https://api.billing.com/invoices")
    .auth
        .bearer_token("abc123")
    .body
        .json({
            "amount": 4900,
            "currency": "usd",
        })
    .reliability
        .timeout_seconds(10)
        .retries(3)
        .idempotency_key("invoice-123")
    .build()
)
```

This is useful because route, auth, body, and reliability are different construction concerns.

The same fluent-cross-facet technique applies:

```text
facet methods return self
facet navigation properties return another facet
build delegates to the root builder
```

---

## 10. Why not just use one big builder?

A single builder is fine when the construction process is only moderately complex.

For example, this may be perfectly readable:

```python
report = (
    ReportBuilder()
    .with_title("Monthly Sales")
    .with_author("Alice")
    .with_summary()
    .with_charts()
    .build()
)
```

Facets may be unnecessary there.

But once the builder starts collecting unrelated areas, it becomes harder to navigate:

```python
CustomerAccountBuilder()
    .named(...)
    .with_email(...)
    .with_billing_address(...)
    .with_vat_number(...)
    .with_card_token(...)
    .enable_email_notifications(...)
    .enable_sms_notifications(...)
    .enable_two_factor_auth(...)
    .enable_login_alerts(...)
```

The faceted version groups the construction language:

```python
.identity.named(...)
.billing.with_card_token(...)
.security.enable_two_factor_auth()
.notifications.enable_sms_notifications()
```

So the decision is not:

> Should every builder be faceted?

The decision is:

> Is this builder getting large because it has distinct categories of construction?

If yes, facets may help.

---

## 11. Advantages

| Advantage | Explanation |
|---|---|
| Better organization | Related construction methods are grouped together. |
| Better readability | `.billing`, `.security`, and `.notifications` reveal intent. |
| Smaller builder classes | Each facet has fewer methods. |
| Clearer responsibilities | Each facet owns one part of construction. |
| Local validation | Each facet validates its own input rules. |
| Global validation | The root builder validates cross-facet rules. |
| Fluent usage | The chain can move across facets without breaking. |

---

## 12. Downsides

Faceted builders add more code.

Instead of one builder, you may have:

```text
root builder
base facet
identity facet
billing facet
notification facet
security facet
```

That is only worth it if the object naturally has multiple construction areas.

Do not use facets for tiny objects.

Bad example:

```python
point = (
    PointBuilder()
    .coordinates
        .x(10)
        .y(20)
    .build()
)
```

This is overengineering.

Prefer:

```python
point = Point(10, 20)
```

Also be careful not to create too many tiny facets. If the categories are artificial, the design becomes harder rather than easier.

---

## 13. Builder facets versus builder inheritance

Builder facets and builder inheritance solve different problems.

| Pattern variation | Use when |
|---|---|
| Builder facets | One complex object has distinct construction areas like identity, billing, security, or layout. |
| Builder inheritance | Your final objects have an inheritance hierarchy, and child builders should reuse parent builder steps. |

Example of builder facets:

```python
CustomerAccountBuilder()
    .identity.named("Alice")
    .billing.with_card_token("tok_123")
    .security.enable_two_factor_auth()
```

Example of builder inheritance:

```python
EmployeeBuilder()
    .named("Alice")       # inherited from PersonBuilder
    .works_as("Engineer") # defined on EmployeeBuilder
```

Builder facets are about **organizing construction areas**.

Builder inheritance is about **specializing builders for subclasses**.

---

## 14. Rule of thumb

Use a regular Builder when you think:

> This object has many construction options.

Use builder facets when you think:

> This builder itself is getting too big, and its methods naturally fall into groups.

Use fluent builder facets when you want this style:

```python
builder.identity.do_one().do_two().billing.do_three().security.do_four().build()
```

The trick is:

```text
methods inside a facet return self
facet navigation properties return another facet from the root builder
build delegates back to the root builder
```

---

## 15. Final summary

Builder facets split a large builder into smaller, focused builders that cooperate to construct the same final object.

A fluent faceted builder gives you both:

- organization through facets,
- smooth chaining across facets.

In one sentence:

> A fluent faceted builder is useful when one complex object has several distinct construction areas, and you want each area to have its own focused builder while still supporting one readable chain of calls.

---

[Root-Builder Inheritance Approach](builder_facets_root_inheritance_approach.md)
