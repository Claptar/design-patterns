---
layout: default
title: Adapter Design Pattern
---

# Adapter Design Pattern

## 1. What problem are we trying to solve?

Imagine your application expects every payment provider to behave like this:

```python
processor.charge(amount_cents=5000, currency="USD")
```

Your own code is clean. It knows one simple idea:

```text
A payment processor can charge money.
```

But then you integrate a third-party provider, and its API looks like this:

```python
stripe_client.create_payment_intent(
    amount=5000,
    currency="usd",
    confirm=True,
)
```

The third-party object works, but it does not have the interface your app expects.

So now you have a mismatch:

```text
Your app expects:        charge(amount_cents, currency)
Third-party object has: create_payment_intent(amount, currency, confirm)
```

You could spread translation logic everywhere:

```python
stripe_client.create_payment_intent(
    amount=amount_cents,
    currency=currency.lower(),
    confirm=True,
)
```

But then your application becomes tightly coupled to Stripe's method names, parameter names, return shape, and quirks.

The problem is:

> We have an object that can do the job, but its interface does not match the interface our code expects.

That is exactly the problem Adapter solves.

---

## 2. Concept introduction

The **Adapter pattern** makes one interface work like another.

In plain English:

> Adapter means: "Wrap an object with an incompatible interface and expose the interface the client expects."

Adapter is a **structural pattern**. Structural patterns are about how classes and objects are composed. They help answer:

> How do I connect objects together cleanly?

The shape is:

```text
Client code
    expects Target interface

Adapter
    exposes Target interface
    internally calls Adaptee

Adaptee
    has useful behavior
    but incompatible interface
```

Vocabulary:

| Term | Meaning |
|---|---|
| Client | The code that wants to use something |
| Target interface | The interface the client expects |
| Adaptee | The existing object with the wrong interface |
| Adapter | The wrapper that translates between them |

---

## 3. First small example

Let us say our application wants this interface:

```python
class PaymentProcessor:
    def charge(self, amount_cents: int, currency: str) -> str:
        raise NotImplementedError
```

Our application code depends on that interface:

```python
class CheckoutService:
    def __init__(self, payment_processor: PaymentProcessor):
        self.payment_processor = payment_processor

    def checkout(self, amount_cents: int):
        payment_id = self.payment_processor.charge(
            amount_cents=amount_cents,
            currency="USD",
        )
        return payment_id
```

Now imagine the third-party class looks different:

```python
class StripeClient:
    def create_payment_intent(self, *, amount: int, currency: str, confirm: bool):
        return {
            "id": "pi_123",
            "amount": amount,
            "currency": currency,
            "status": "succeeded" if confirm else "requires_confirmation",
        }
```

It can charge money, but it does not have `.charge(...)`.

So we add an adapter:

```python
class StripePaymentAdapter(PaymentProcessor):
    def __init__(self, stripe_client: StripeClient):
        self._stripe_client = stripe_client

    def charge(self, amount_cents: int, currency: str) -> str:
        result = self._stripe_client.create_payment_intent(
            amount=amount_cents,
            currency=currency.lower(),
            confirm=True,
        )

        return result["id"]
```

Now the application can use Stripe through the interface it already understands:

```python
stripe_client = StripeClient()
payment_processor = StripePaymentAdapter(stripe_client)

checkout = CheckoutService(payment_processor)
payment_id = checkout.checkout(5000)

print(payment_id)  # pi_123
```

The important thing is that `CheckoutService` does not know about `create_payment_intent`.

It only knows:

```python
payment_processor.charge(...)
```

The adapter absorbs the mismatch.

---

## 4. What actually changed?

Before Adapter:

```text
CheckoutService
    directly understands StripeClient
    directly calls create_payment_intent
    directly knows Stripe-specific details
```

After Adapter:

```text
CheckoutService
    understands PaymentProcessor

StripePaymentAdapter
    understands both PaymentProcessor and StripeClient

StripeClient
    remains unchanged
```

The adapter becomes the translation layer.

```text
charge(amount_cents, currency)
        |
        v
create_payment_intent(amount=..., currency=..., confirm=True)
```

That is the core mechanism.

---

## 5. Natural example: importing customers from an old system

Suppose your application expects customer importers to return a list of dictionaries:

```python
class CustomerImporter:
    def import_customers(self, path: str) -> list[dict]:
        raise NotImplementedError
```

Your app uses it like this:

```python
def import_customer_emails(importer: CustomerImporter, path: str) -> list[str]:
    customers = importer.import_customers(path)
    return [customer["email"] for customer in customers]
```

Now your company buys an old ERP system. Its Python client already exists, but it looks like this:

```python
class LegacyErpClient:
    def load_people(self, filename: str):
        return [
            ("Alice", "ALICE@EXAMPLE.COM"),
            ("Bob", "BOB@EXAMPLE.COM"),
        ]
```

It gives tuples.

Your app wants dictionaries.

You could rewrite your app to understand tuples, but that spreads legacy knowledge everywhere.

Instead, write an adapter:

```python
class LegacyErpCustomerImporter(CustomerImporter):
    def __init__(self, erp_client: LegacyErpClient):
        self._erp_client = erp_client

    def import_customers(self, path: str) -> list[dict]:
        people = self._erp_client.load_people(path)

        return [
            {
                "name": name.strip(),
                "email": email.strip().lower(),
            }
            for name, email in people
        ]
```

Usage:

```python
erp_client = LegacyErpClient()
importer = LegacyErpCustomerImporter(erp_client)

emails = import_customer_emails(importer, "customers.dat")

print(emails)
# ['alice@example.com', 'bob@example.com']
```

Now the rest of the system does not care that the old ERP client returns tuples.

The adapter turns legacy shape into application shape.

---

## 6. Adapter and validation/normalization

Adapters often do more than rename methods.

They may also translate:

```text
method names
argument names
argument order
units
case conventions
return values
exceptions
data structures
sync/async boundaries
old API versions
```

Example:

```python
currency="USD"
```

may become:

```python
currency="usd"
```

A tuple:

```python
("Alice", "ALICE@EXAMPLE.COM")
```

may become:

```python
{"name": "Alice", "email": "alice@example.com"}
```

A provider-specific exception:

```python
StripeCardError
```

may become your application exception:

```python
PaymentDeclined
```

So Adapter is often about protecting the rest of your code from external weirdness.

---

## 7. Connection to earlier learned concepts

### Adapter versus Factory

A **Factory** decides which object to create.

Adapter answers a different question:

| Pattern | Main question |
|---|---|
| Factory | Which object should I create? |
| Adapter | How do I make this object fit the interface I need? |

They often work together:

```python
def create_payment_processor(provider: str) -> PaymentProcessor:
    if provider == "stripe":
        return StripePaymentAdapter(StripeClient())

    if provider == "paypal":
        return PayPalPaymentAdapter(PayPalClient())

    raise ValueError(f"Unknown provider: {provider}")
```

The factory chooses.

The adapter makes the chosen object usable.

### Adapter versus Builder

Builder is about assembling a complex object step by step.

Adapter is not mainly about constructing an object.

It is about connecting already-existing objects whose interfaces do not match.

| Pattern | Main job |
|---|---|
| Builder | Assemble an object correctly |
| Adapter | Translate one interface into another |

### Adapter versus Singleton

Singleton controls object identity: should there be only one instance?

Adapter does not care how many instances exist.

You can have:

```python
stripe_adapter_1 = StripePaymentAdapter(StripeClient())
stripe_adapter_2 = StripePaymentAdapter(StripeClient())
```

That is fine.

Adapter's concern is interface compatibility, not uniqueness.

### Adapter and SOLID

Adapter connects strongly to **Dependency Inversion**.

Without Adapter:

```python
class CheckoutService:
    def __init__(self):
        self.stripe_client = StripeClient()
```

Now `CheckoutService` depends directly on Stripe.

With Adapter:

```python
class CheckoutService:
    def __init__(self, payment_processor: PaymentProcessor):
        self.payment_processor = payment_processor
```

Now `CheckoutService` depends on your abstraction.

Stripe-specific details are pushed outward into `StripePaymentAdapter`.

Adapter also helps **Single Responsibility Principle**:

```text
CheckoutService handles checkout.
StripePaymentAdapter handles Stripe translation.
StripeClient handles Stripe API calls.
```

Each class has a clearer job.

---

## 8. Example from a popular Python package: scikit-learn

A good data-science example is `sklearn.preprocessing.FunctionTransformer`.

In scikit-learn, pipeline intermediate steps must be transformers, meaning they must implement `fit` and `transform`.

But sometimes you just have a normal Python function:

```python
import numpy as np

def log_transform(X):
    return np.log1p(X)
```

That function is useful, but it does not have the scikit-learn transformer interface:

```python
.fit(...)
.transform(...)
```

`FunctionTransformer` adapts that callable into a transformer. The official docs describe it as constructing a transformer from an arbitrary callable and forwarding `X` to the user-defined function.

Example:

```python
import numpy as np
from sklearn.preprocessing import FunctionTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression

log_transformer = FunctionTransformer(np.log1p)

pipeline = Pipeline([
    ("log", log_transformer),
    ("model", LinearRegression()),
])
```

Here is the adapter idea:

```text
Normal function:
    np.log1p(X)

Scikit-learn expects:
    transformer.fit(X, y)
    transformer.transform(X)

FunctionTransformer:
    wraps the function
    exposes the transformer interface
```

So `FunctionTransformer` acts like an adapter:

```text
arbitrary callable -> scikit-learn transformer
```

That is a very natural Adapter-shaped design.

References:

- <https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html>
- <https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.FunctionTransformer.html>

---

## 9. Adapter versus similar patterns

### Adapter versus Decorator

Decorator keeps the same interface and adds behavior.

```text
Original object:
    send(message)

Decorator:
    send(message) but also logs, retries, caches, etc.
```

Adapter changes the interface.

```text
Original object:
    create_payment_intent(...)

Adapter:
    charge(...)
```

Use Decorator when the interface already fits, but you want extra behavior.

Use Adapter when the behavior exists, but the interface does not fit.

### Adapter versus Facade

Facade simplifies a complex subsystem.

```text
Many complicated subsystem calls
        |
        v
one simpler interface
```

Adapter makes one interface compatible with another.

```text
Existing incompatible object
        |
        v
expected interface
```

A facade says:

> This subsystem is too complicated; give me a simpler doorway.

An adapter says:

> This object speaks the wrong language; translate it for me.

---

## 10. When to use Adapter

Use Adapter when:

| Situation | Why Adapter helps |
|---|---|
| You use a third-party library with a different API | Keeps library-specific details out of your core code |
| You integrate a legacy system | Converts old shapes into current shapes |
| You want your app to depend on your own interface | Supports dependency inversion |
| You need to normalize return values | Keeps normalization in one place |
| You want several providers to look the same | Stripe, PayPal, Adyen, etc. can all become `PaymentProcessor` |
| You want tests to use fake implementations | Tests can provide a fake object with the same target interface |

---

## 11. When not to use Adapter

Do not use Adapter when the object already has the interface you need.

Bad:

```python
class UserRepositoryAdapter:
    def __init__(self, repository):
        self.repository = repository

    def save(self, user):
        return self.repository.save(user)
```

If this adapter only forwards the same method with the same arguments, it adds no value.

Also avoid Adapter when you own both sides and can simply improve the original interface.

For example, if `LegacyErpClient` is not really legacy and your team controls it, maybe just rename or redesign the method directly.

Use Adapter when changing the adaptee is hard, risky, impossible, or undesirable.

---

## 12. Practical rule of thumb

Ask:

> Do I have useful behavior behind the wrong interface?

If yes, Adapter may help.

Ask:

> Am I translating method names, argument shapes, return values, exceptions, or units?

If yes, Adapter is probably a good fit.

Ask:

> Am I just wrapping a method with the same method?

If yes, Adapter is probably unnecessary.

Ask:

> Does my core code know too much about a third-party API?

If yes, put an adapter between them.

---

## 13. Summary and mental model

Adapter is a structural pattern for interface mismatch.

The mental model:

```text
Power socket adapter:

Your laptop plug does not fit the wall socket.
The wall has power.
The laptop needs power.
The adapter does not create electricity.
It only makes the connection compatible.
```

In code:

```text
Client expects Target interface.
Adaptee has useful behavior but wrong interface.
Adapter wraps Adaptee and exposes Target.
```

One-sentence summary:

> Adapter lets existing code work with an incompatible object by wrapping that object and translating calls into the interface the client expects.
