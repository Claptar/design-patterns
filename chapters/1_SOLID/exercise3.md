---
layout: default
title: "SOLID Exercise 3: Subscription Billing"
---

# SOLID Exercise 3: Subscription Billing

## Scenario

A SaaS product bills customers monthly. The current implementation looks like this:

```python
class BillingService:
    def bill_customer(self, customer, plan, usage):
        # Check whether customer can be billed
        if not customer.is_active:
            raise ValueError("Inactive customers cannot be billed")

        if customer.payment_method is None:
            raise ValueError("Customer has no payment method")

        # Calculate base price
        if plan.name == "free":
            amount = 0

        elif plan.name == "starter":
            amount = 19

        elif plan.name == "pro":
            amount = 49

        elif plan.name == "enterprise":
            amount = 499

        else:
            raise ValueError("Unknown plan")

        # Add usage charges
        if usage.api_calls > plan.included_api_calls:
            extra_calls = usage.api_calls - plan.included_api_calls
            amount += extra_calls * 0.01

        if usage.storage_gb > plan.included_storage_gb:
            extra_storage = usage.storage_gb - plan.included_storage_gb
            amount += extra_storage * 0.25

        # Apply discounts
        if customer.is_nonprofit:
            amount *= 0.8

        if customer.has_annual_contract:
            amount *= 0.9

        if customer.coupon_code == "WELCOME10":
            amount *= 0.9

        # Charge payment provider
        if customer.payment_provider == "stripe":
            stripe = StripeClient()
            charge_id = stripe.charge(customer.payment_method, amount)

        elif customer.payment_provider == "paypal":
            paypal = PayPalClient()
            charge_id = paypal.charge(customer.payment_method, amount)

        else:
            raise ValueError("Unsupported payment provider")

        # Send receipt
        email = EmailSender()
        email.send(
            customer.email,
            "Your monthly invoice",
            f"You were charged ${amount}"
        )

        # Record invoice
        database = PostgresDatabase()
        database.save_invoice({
            "customer_id": customer.id,
            "plan": plan.name,
            "amount": amount,
            "charge_id": charge_id
        })

        return charge_id
```

## Exercise Prompt

Critique this design using SOLID.

Try to answer:

1. Which SOLID principles might this violate?
2. What are the main design smells?
3. What would you change?
4. Which parts are okay as-is?
5. Would you fully split this design, or use a middle-ground refactor first?

## Your Critique

- Validation, business logic, and sending receipts are mixed together, which suggests a Single Responsibility Principle violation.
- Different plans are handled with conditional logic, which suggests an Open/Closed Principle issue.
- Different charging schemes are embedded in the business logic, which also suggests an Open/Closed Principle issue.
- Different payment providers are handled with conditionals, another Open/Closed Principle issue.
- Recording the invoice directly through a concrete database dependency breaks Dependency Inversion.
- You initially suggested email sending was fine according to Dependency Inversion. The corrected version is: sending a receipt is fine as part of the workflow, but directly creating `EmailSender()` is a Dependency Inversion smell.

---

# Full Critique

## Overall Verdict

`BillingService.bill_customer()` has become a large, central method that knows too much. It handles billing eligibility, plan pricing, usage pricing, discounts, payment provider selection, receipt sending, invoice persistence, and dependency creation.

The workflow itself is reasonable:

```text
validate customer
calculate amount
charge customer
send receipt
record invoice
return charge ID
```

The problem is that the details of every step are all inside one method. That makes the code harder to extend, harder to test, and riskier to change.

---

## 1. Single Responsibility Principle

This method has many reasons to change:

| Responsibility | Example |
|---|---|
| Billing validation | inactive customer, missing payment method |
| Plan pricing | free, starter, pro, enterprise |
| Usage pricing | API calls, storage |
| Discounts | nonprofit, annual contract, coupon |
| Payment processing | Stripe, PayPal |
| Receipts | email content and delivery |
| Invoice persistence | database save format |

That means it violates the Single Responsibility Principle.

A cleaner split could be:

```python
class BillingValidator:
    def validate(self, customer, plan):
        ...


class PriceCalculator:
    def calculate(self, customer, plan, usage):
        ...


class PaymentProcessor:
    def charge(self, payment_method, amount):
        ...


class ReceiptSender:
    def send_receipt(self, customer, amount):
        ...


class InvoiceRepository:
    def save_invoice(self, invoice):
        ...
```

Then `BillingService` can coordinate the flow instead of containing every implementation detail.

```python
class BillingService:
    def __init__(
        self,
        validator,
        price_calculator,
        payment_processors,
        receipt_sender,
        invoice_repository
    ):
        self.validator = validator
        self.price_calculator = price_calculator
        self.payment_processors = payment_processors
        self.receipt_sender = receipt_sender
        self.invoice_repository = invoice_repository

    def bill_customer(self, customer, plan, usage):
        self.validator.validate(customer, plan)

        amount = self.price_calculator.calculate(customer, plan, usage)

        processor = self.payment_processors[customer.payment_provider]
        charge_id = processor.charge(customer.payment_method, amount)

        self.receipt_sender.send_receipt(customer, amount)

        self.invoice_repository.save_invoice({
            "customer_id": customer.id,
            "plan": plan.name,
            "amount": amount,
            "charge_id": charge_id,
        })

        return charge_id
```

Important distinction: `BillingService` can still coordinate multiple steps. SRP does not mean a method can only call one thing. It means the method should not personally own unrelated details.

---

## 2. Open/Closed Principle

There are several Open/Closed Principle issues.

### Plan Pricing

This block is not open for extension:

```python
if plan.name == "free":
    amount = 0
elif plan.name == "starter":
    amount = 19
elif plan.name == "pro":
    amount = 49
elif plan.name == "enterprise":
    amount = 499
else:
    raise ValueError("Unknown plan")
```

Adding a new plan, such as `team`, `business`, `education`, or `enterprise_plus`, requires editing `BillingService`.

For simple fixed prices, a dictionary may be enough:

```python
PLAN_PRICES = {
    "free": 0,
    "starter": 19,
    "pro": 49,
    "enterprise": 499,
}
```

For complex pricing, separate pricing strategies may be better.

```python
class StarterPlanPricing:
    def base_price(self):
        return 19


class ProPlanPricing:
    def base_price(self):
        return 49
```

Do not create a class per plan automatically. A dictionary is often the better design while pricing is simple.

### Usage Pricing

This part may also become an Open/Closed issue:

```python
if usage.api_calls > plan.included_api_calls:
    extra_calls = usage.api_calls - plan.included_api_calls
    amount += extra_calls * 0.01

if usage.storage_gb > plan.included_storage_gb:
    extra_storage = usage.storage_gb - plan.included_storage_gb
    amount += extra_storage * 0.25
```

Two usage dimensions are manageable. But if the product later adds seats, bandwidth, AI tokens, projects, team members, custom domains, or build minutes, this method will keep growing.

A more extensible design could use charge rules:

```python
class ApiCallUsageCharge:
    def calculate(self, plan, usage):
        ...


class StorageUsageCharge:
    def calculate(self, plan, usage):
        ...
```

Then:

```python
amount += sum(rule.calculate(plan, usage) for rule in usage_charge_rules)
```

Adding a new usage charge becomes adding a new rule instead of editing the billing method.

### Discounts

This block is another Open/Closed smell:

```python
if customer.is_nonprofit:
    amount *= 0.8

if customer.has_annual_contract:
    amount *= 0.9

if customer.coupon_code == "WELCOME10":
    amount *= 0.9
```

Every new discount requires editing the method.

A cleaner design could use discount policies:

```python
class NonprofitDiscount:
    def apply(self, customer, amount):
        if customer.is_nonprofit:
            return amount * 0.8
        return amount


class AnnualContractDiscount:
    def apply(self, customer, amount):
        if customer.has_annual_contract:
            return amount * 0.9
        return amount


class WelcomeCouponDiscount:
    def apply(self, customer, amount):
        if customer.coupon_code == "WELCOME10":
            return amount * 0.9
        return amount
```

Then:

```python
for discount in discounts:
    amount = discount.apply(customer, amount)
```

Be careful, though. Discounts often have ordering rules, stacking rules, caps, exclusions, and expiry dates. That may justify a dedicated discount engine or pricing policy later.

### Payment Providers

This is also an Open/Closed violation:

```python
if customer.payment_provider == "stripe":
    stripe = StripeClient()
    charge_id = stripe.charge(customer.payment_method, amount)

elif customer.payment_provider == "paypal":
    paypal = PayPalClient()
    charge_id = paypal.charge(customer.payment_method, amount)
```

Adding Adyen, Braintree, Apple Pay, bank debit, or manual invoicing requires editing `BillingService`.

A better design would use payment processor implementations:

```python
class StripePaymentProcessor:
    def charge(self, payment_method, amount):
        ...


class PayPalPaymentProcessor:
    def charge(self, payment_method, amount):
        ...
```

Then use a registry:

```python
processor = payment_processors[customer.payment_provider]
charge_id = processor.charge(customer.payment_method, amount)
```

---

## 3. Dependency Inversion Principle

The code directly creates concrete dependencies:

```python
stripe = StripeClient()
paypal = PayPalClient()
email = EmailSender()
database = PostgresDatabase()
```

That violates the Dependency Inversion Principle because high-level billing logic depends directly on low-level implementation details.

Problems:

```text
Hard to unit test without Stripe, PayPal, email, or database behavior.
Hard to replace providers.
Hard to run billing in dry-run mode.
Hard to simulate failures.
Business logic is coupled to infrastructure choices.
```

The act of sending a receipt is not the problem. This is a normal part of the billing workflow. The problem is that `BillingService` directly creates a concrete `EmailSender`.

A better design injects dependencies:

```python
class BillingService:
    def __init__(
        self,
        validator,
        price_calculator,
        payment_processors,
        receipt_sender,
        invoice_repository
    ):
        ...
```

Production wiring can use real implementations:

```python
service = BillingService(
    validator=BillingValidator(),
    price_calculator=PriceCalculator(...),
    payment_processors={
        "stripe": StripePaymentProcessor(StripeClient()),
        "paypal": PayPalPaymentProcessor(PayPalClient()),
    },
    receipt_sender=EmailReceiptSender(EmailSender()),
    invoice_repository=PostgresInvoiceRepository(PostgresDatabase()),
)
```

Tests can use fakes:

```python
service = BillingService(
    validator=FakeValidator(),
    price_calculator=FakePriceCalculator(amount=49),
    payment_processors={"stripe": FakePaymentProcessor()},
    receipt_sender=FakeReceiptSender(),
    invoice_repository=FakeInvoiceRepository(),
)
```

---

## 4. Interface Segregation Principle

There is no direct Interface Segregation Principle violation shown because no explicit interface is present.

However, ISP becomes important during refactoring. A bad refactor would create one giant abstraction:

```python
class BillingInfrastructure:
    def validate_customer(self, customer):
        ...

    def calculate_price(self, customer, plan, usage):
        ...

    def charge_stripe(self, payment_method, amount):
        ...

    def charge_paypal(self, payment_method, amount):
        ...

    def send_email(self, customer, amount):
        ...

    def save_invoice(self, invoice):
        ...
```

That would just move the mess into a large interface.

Better to use focused contracts:

```python
class BillingValidator:
    def validate(self, customer, plan):
        ...


class PriceCalculator:
    def calculate(self, customer, plan, usage):
        ...


class PaymentProcessor:
    def charge(self, payment_method, amount):
        ...


class ReceiptSender:
    def send_receipt(self, customer, amount):
        ...


class InvoiceRepository:
    def save_invoice(self, invoice):
        ...
```

Each collaborator depends only on the methods it actually needs.

---

## 5. Liskov Substitution Principle

No direct Liskov Substitution Principle violation appears in the original code because there is no inheritance or subtype relationship.

But LSP matters once abstractions are introduced.

For example, suppose all payment processors use this contract:

```python
class PaymentProcessor:
    def charge(self, payment_method, amount):
        """Charge the customer and return a charge ID."""
```

This implementation may break substitutability:

```python
class ManualInvoiceProcessor(PaymentProcessor):
    def charge(self, payment_method, amount):
        return None
```

If the rest of the billing flow expects a real `charge_id`, then `ManualInvoiceProcessor` is not safely substitutable.

A better design may need a richer result object:

```python
class PaymentResult:
    def __init__(self, status, charge_id=None):
        self.status = status
        self.charge_id = charge_id
```

Free plans create a similar issue. If amount is zero, should the system call a payment provider at all? If payment processors assume a positive amount, then a zero-dollar charge may break some implementations.

---

# Additional Design Smells

## Charging Happens Before Invoice Recording

Current order:

```text
charge customer
send receipt
record invoice
return charge ID
```

This is risky. If Stripe charges successfully but the database save fails, the customer was charged but no invoice was recorded.

A safer workflow might be:

```text
create pending invoice
charge customer
mark invoice as paid
send receipt
```

Example:

```python
invoice = invoice_repository.create_pending_invoice(customer, plan, amount)

try:
    payment_result = payment_processor.charge(customer.payment_method, amount)
    invoice_repository.mark_paid(invoice.id, payment_result.charge_id)
    receipt_sender.send_receipt(customer, invoice, payment_result)
    return payment_result.charge_id
except Exception:
    invoice_repository.mark_failed(invoice.id)
    raise
```

Billing systems need careful failure handling because money may move even if later steps fail.

## Receipt Sending Should Not Usually Decide Whether Billing Succeeded

If payment succeeds but the receipt email fails, should billing fail?

Usually, no. The charge already happened.

Receipt sending may be better as a secondary side effect or event handler:

```python
event_bus.publish(CustomerBilled(invoice_id=invoice.id))
```

For a small system, synchronous email may be acceptable. But the design should be clear about whether email failure affects billing success.

## Money Should Not Use Floats

This code uses floating-point arithmetic:

```python
amount += extra_calls * 0.01
amount += extra_storage * 0.25
amount *= 0.8
```

For money, this is risky because floating-point arithmetic can introduce rounding errors.

A real billing system should use either `Decimal`:

```python
from decimal import Decimal
```

or integer cents:

```python
amount_cents = 4900
```

This is not a SOLID issue, but it is a serious correctness issue.

## Discount Order May Matter

Discounts are applied sequentially:

```python
if customer.is_nonprofit:
    amount *= 0.8

if customer.has_annual_contract:
    amount *= 0.9

if customer.coupon_code == "WELCOME10":
    amount *= 0.9
```

This means discounts stack multiplicatively.

On `$100`, the result would be:

```text
nonprofit: 100 -> 80
annual: 80 -> 72
coupon: 72 -> 64.80
```

Maybe that is correct. Maybe not. Business rules may require only one discount, best discount wins, coupons cannot combine with nonprofit pricing, annual discount applies only to base price, or coupons have expiry dates.

Discount behavior should be explicit and tested.

## Free Plans May Reveal a Business Rule Bug

For the free plan:

```python
amount = 0
```

But the code still requires a payment method:

```python
if customer.payment_method is None:
    raise ValueError("Customer has no payment method")
```

And it still attempts to charge:

```python
charge_id = stripe.charge(customer.payment_method, amount)
```

Maybe free customers are required to have a payment method. But if not, this is a bug.

The flow may need to support zero-dollar invoices:

```text
If amount is 0, do not require payment method.
Create invoice as paid/free.
Do not call payment provider.
Send free-plan confirmation or invoice receipt.
```

---

# Which Parts Are Okay?

The high-level workflow is okay:

```text
validate
price
charge
receipt
record
```

The validation checks themselves are readable:

```python
if not customer.is_active:
    raise ValueError("Inactive customers cannot be billed")

if customer.payment_method is None:
    raise ValueError("Customer has no payment method")
```

The plan pricing block is acceptable for a tiny prototype with stable plans.

The usage pricing block is understandable while there are only two usage dimensions.

The code is not unreadable yet. The issue is that it will become brittle as billing becomes more realistic.

---

# Full Refactor Direction

A fuller refactor could look like this:

```python
class BillingService:
    def __init__(
        self,
        validator,
        price_calculator,
        payment_processors,
        invoice_repository,
        receipt_sender
    ):
        self.validator = validator
        self.price_calculator = price_calculator
        self.payment_processors = payment_processors
        self.invoice_repository = invoice_repository
        self.receipt_sender = receipt_sender

    def bill_customer(self, customer, plan, usage):
        self.validator.validate(customer, plan)

        amount = self.price_calculator.calculate(customer, plan, usage)

        invoice = self.invoice_repository.create_pending_invoice(
            customer=customer,
            plan=plan,
            amount=amount
        )

        if amount == 0:
            self.invoice_repository.mark_paid(invoice.id, charge_id=None)
            self.receipt_sender.send_receipt(customer, invoice)
            return None

        processor = self.payment_processors[customer.payment_provider]

        try:
            charge_id = processor.charge(customer.payment_method, amount)
            self.invoice_repository.mark_paid(invoice.id, charge_id)
            self.receipt_sender.send_receipt(customer, invoice)
            return charge_id
        except Exception:
            self.invoice_repository.mark_failed(invoice.id)
            raise
```

This gives each concern a place:

| Concern | Component |
|---|---|
| Can this customer be billed? | `BillingValidator` |
| How much should they pay? | `PriceCalculator` |
| How do we charge them? | `PaymentProcessor` |
| How do we record invoices? | `InvoiceRepository` |
| How do we send receipts? | `ReceiptSender` |

---

# Middle-Ground Refactor

A full split may be too much immediately.

A good middle-ground version would keep one `BillingService`, but extract the most volatile pieces:

```python
class BillingService:
    def __init__(self, payment_processors, email_sender, invoice_repository):
        self.payment_processors = payment_processors
        self.email_sender = email_sender
        self.invoice_repository = invoice_repository

    def bill_customer(self, customer, plan, usage):
        self._validate(customer)

        amount = self._calculate_amount(customer, plan, usage)

        processor = self.payment_processors[customer.payment_provider]
        charge_id = processor.charge(customer.payment_method, amount)

        self.email_sender.send(
            customer.email,
            "Your monthly invoice",
            f"You were charged ${amount}"
        )

        self.invoice_repository.save_invoice({
            "customer_id": customer.id,
            "plan": plan.name,
            "amount": amount,
            "charge_id": charge_id,
        })

        return charge_id

    def _validate(self, customer):
        if not customer.is_active:
            raise ValueError("Inactive customers cannot be billed")

        if customer.payment_method is None:
            raise ValueError("Customer has no payment method")

    def _calculate_amount(self, customer, plan, usage):
        prices = {
            "free": 0,
            "starter": 19,
            "pro": 49,
            "enterprise": 499,
        }

        try:
            amount = prices[plan.name]
        except KeyError:
            raise ValueError("Unknown plan")

        if usage.api_calls > plan.included_api_calls:
            amount += (usage.api_calls - plan.included_api_calls) * 0.01

        if usage.storage_gb > plan.included_storage_gb:
            amount += (usage.storage_gb - plan.included_storage_gb) * 0.25

        if customer.is_nonprofit:
            amount *= 0.8

        if customer.has_annual_contract:
            amount *= 0.9

        if customer.coupon_code == "WELCOME10":
            amount *= 0.9

        return amount
```

This middle-ground refactor improves:

```text
DIP: dependencies are injected
OCP: payment providers are pluggable
Readability: validation and pricing are named methods
Testability: payment, email, and database can be faked
```

But it does not fully solve:

```text
OCP for plans
OCP for discounts
OCP for usage charge types
SRP around pricing logic
billing transaction reliability
```

This is often a realistic first step before splitting pricing into its own module.

---

# Summary

| Principle | Critique |
|---|---|
| SRP | Violated. Billing, pricing, discounts, payments, receipts, and persistence are all mixed. |
| OCP | Violated. New plans, usage charges, discounts, and payment providers require modifying the method. |
| DIP | Violated. The service directly creates Stripe, PayPal, email, and database dependencies. |
| ISP | Not directly visible. Be careful not to refactor into one giant billing interface. |
| LSP | Not directly visible. Becomes important when payment/pricing abstractions are introduced. |

Main corrections to the initial critique:

```text
Email sending is part of the workflow, but directly creating EmailSender violates DIP.
Recording the invoice violates DIP because PostgresDatabase is created directly.
Free-plan billing may reveal a deeper business-rule bug.
Payment success should probably be recorded more carefully before and after charging.
```

A clean design would keep `BillingService` as the workflow coordinator and move pricing, payment, receipt, and persistence details into focused collaborators.
