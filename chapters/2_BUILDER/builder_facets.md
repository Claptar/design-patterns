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

## 3. Important fluent-design idea

Inside a facet, methods usually return `self`:

```python
def named(self, name):
    self._account.name = name
    return self
```

That lets you chain methods inside the same facet:

```python
.identity.named("Alice").with_email("alice@example.com")
```

But to move between facets fluently, each facet also needs access to the other facets:

```python
.identity.named("Alice").billing.with_card_token("tok_123")
```

So each facet can expose properties that delegate back to the root builder:

```python
@property
def billing(self):
    return self._root.billing
```

That gives us fluent chaining across facets.

---

## 4. Full fluent faceted builder example

### Final object

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

The final object is simple. It only stores the completed data.

---

## 5. Root builder

The root builder owns the object being built and exposes each facet.

```python
class CustomerAccountBuilder:
    def __init__(self):
        self._account = CustomerAccount()

        self._identity = IdentityBuilder(self, self._account)
        self._billing = BillingBuilder(self, self._account)
        self._notifications = NotificationBuilder(self, self._account)
        self._security = SecurityBuilder(self, self._account)

    @property
    def identity(self):
        return self._identity

    @property
    def billing(self):
        return self._billing

    @property
    def notifications(self):
        return self._notifications

    @property
    def security(self):
        return self._security

    def build(self):
        if not self._account.name:
            raise ValueError("Name is required")

        if not self._account.email:
            raise ValueError("Email is required")

        if self._account.sms_notifications and not self._account.two_factor_auth:
            raise ValueError("SMS notifications require two-factor authentication")

        return self._account
```

The root builder handles validation that involves multiple facets.

For example, `SMS notifications require two-factor authentication` involves both notifications and security, so it belongs in the root builder.

---

## 6. Base facet helper

To avoid repeating the same navigation properties in every facet, we can create a small base class.

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
    def notifications(self):
        return self._root.notifications

    @property
    def security(self):
        return self._root.security

    def build(self):
        return self._root.build()
```

This is what allows cross-facet chaining:

```python
.identity.named("Alice").billing.with_card_token("tok_123").build()
```

Each facet can return itself for methods within the facet, while also exposing other facets through properties.

---

## 7. Identity facet

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

This facet owns identity-specific construction rules:

```text
name cannot be blank
email should be normalized
email should look valid
```

---

## 8. Billing facet

```python
class BillingBuilder(BuilderFacet):
    def with_billing_address(self, address):
        if not address.strip():
            raise ValueError("Billing address cannot be blank")

        self._account.billing_address = address.strip()
        return self

    def with_vat_number(self, vat_number):
        self._account.vat_number = vat_number.strip().upper()
        return self

    def with_card_token(self, card_token):
        if not card_token.startswith("tok_"):
            raise ValueError("Card token must start with 'tok_'")

        self._account.card_token = card_token
        return self
```

This facet owns billing-related setup and validation.

---

## 9. Notification facet

```python
class NotificationBuilder(BuilderFacet):
    def enable_email_notifications(self):
        self._account.email_notifications = True
        return self

    def enable_sms_notifications(self):
        self._account.sms_notifications = True
        return self

    def disable_all_notifications(self):
        self._account.email_notifications = False
        self._account.sms_notifications = False
        return self
```

This facet only deals with notification preferences.

---

## 10. Security facet

```python
class SecurityBuilder(BuilderFacet):
    def enable_two_factor_auth(self):
        self._account.two_factor_auth = True
        return self

    def disable_two_factor_auth(self):
        self._account.two_factor_auth = False
        return self

    def enable_login_alerts(self):
        self._account.login_alerts = True
        return self
```

This facet owns security-related setup.

---

## 11. Fully fluent usage

Now you can fluently move across facets:

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

This works because:

- `named()` returns the identity facet itself.
- `with_email()` returns the identity facet itself.
- `.billing` is a property available on the identity facet through `BuilderFacet`.
- billing methods return the billing facet.
- `.security` moves from billing to security.
- `.notifications` moves from security to notifications.
- `.build()` delegates back to the root builder.

---

## 12. Local validation versus global validation

Builder facets are useful because validation can be split naturally.

### Local validation

Local validation belongs inside a facet.

Example:

```python
def with_card_token(self, card_token):
    if not card_token.startswith("tok_"):
        raise ValueError("Card token must start with 'tok_'")

    self._account.card_token = card_token
    return self
```

This rule is purely about billing.

### Global validation

Global validation belongs in the root builder.

Example:

```python
def build(self):
    if self._account.sms_notifications and not self._account.two_factor_auth:
        raise ValueError("SMS notifications require two-factor authentication")

    return self._account
```

This rule involves two facets: notifications and security.

---

## 13. Why not just use one big builder?

A single builder is fine when the construction process is moderately complex.

But once the builder methods naturally fall into groups, one big builder can become hard to navigate:

```python
CustomerAccountBuilder
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

This improves readability and keeps each builder class smaller.

---

## 14. Another fluent example: HTTP request facets

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

The same fluent-cross-facet technique works:

- facet methods return `self`
- facets expose other facets through properties
- `build()` delegates to the root builder

---

## 15. Advantages

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

## 16. Downsides

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

---

## 17. Regular Builder versus Faceted Builder

| Question | Regular Builder | Faceted Builder |
|---|---|---|
| Main problem | Object has many construction steps. | Object has many construction steps across different categories. |
| Structure | One builder. | Root builder plus smaller facet builders. |
| Best for | Moderately complex objects. | Large objects with distinct configuration areas. |
| Risk | Builder becomes too large. | Too many small builder classes. |
| Example | `ReportBuilder` | `CustomerAccountBuilder.identity.billing.security` |

---

## 18. Rule of thumb

Use a regular Builder when you think:

> This object has many construction options.

Use builder facets when you think:

> This builder itself is getting too big, and its methods naturally fall into groups.

Use fluent builder facets when you want:

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

## 19. Final summary

Builder facets split a large builder into smaller, focused builders that cooperate to construct the same final object.

A fluent faceted builder gives you both:

- organization through facets
- smooth chaining across facets

In one sentence:

> A fluent faceted builder is useful when one complex object has several distinct construction areas, and you want each area to have its own focused builder while still supporting one readable chain of calls.
