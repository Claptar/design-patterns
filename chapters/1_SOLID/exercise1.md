# SOLID Design Exercise1: Order Notifications

## Scenario

A small ecommerce app has this implementation:

```python
class OrderService:
    def place_order(self, order):
        # Validate order
        if not order.items:
            raise ValueError("Order must contain at least one item")

        if order.total <= 0:
            raise ValueError("Order total must be positive")

        # Save order
        database = MySQLDatabase()
        database.save(order)

        # Send notification
        if order.customer.preferred_notification == "email":
            email_sender = EmailSender()
            email_sender.send(
                order.customer.email,
                "Order confirmed",
                "Thanks for your order!"
            )

        elif order.customer.preferred_notification == "sms":
            sms_sender = SmsSender()
            sms_sender.send(
                order.customer.phone_number,
                "Thanks for your order!"
            )

        elif order.customer.preferred_notification == "push":
            push_sender = PushSender()
            push_sender.send(
                order.customer.device_id,
                "Order confirmed"
            )

        # Track analytics
        analytics = AnalyticsClient()
        analytics.track("order_placed", {
            "order_id": order.id,
            "total": order.total,
            "customer_id": order.customer.id
        })
```

Full original implementation file: [exercise1.py](chapters/1_SOLID/exercise1.py)

Fixed implementation file: [exercise1_fixed.py](chapters/1_SOLID/exercies1_fixed.py)

---

## Exercise Prompt

Critique this design using the SOLID principles.

Try to answer:

1. Which SOLID principles might this violate?
2. What are the main design smells?
3. What would you change?
4. Which parts are okay as-is?

---

## Initial Student Critique

1. Order validation, persistence, notification, and analytics should be separate. This is a Single Responsibility Principle violation.
2. The three different notification senders suggest an Open/Closed Principle issue.
3. Database details are exposed, which suggests a Dependency Inversion Principle issue.

---

## Full Critique

### Overall verdict

This design works for a small prototype, but it mixes too many responsibilities and hard-codes too many implementation details into `OrderService`.

`OrderService` has become an orchestration method, validation layer, persistence layer, notification dispatcher, analytics tracker, and dependency creator all at once.

---

## 1. Single Responsibility Principle

The initial critique is correct.

```python
class OrderService:
    def place_order(self, order):
        # validate
        # save
        # notify
        # track analytics
```

This class has several reasons to change:

| Reason for change | Code affected |
|---|---|
| Order validation rules change | `OrderService` |
| Database changes | `OrderService` |
| Notification rules change | `OrderService` |
| Analytics event schema changes | `OrderService` |
| Order placement business flow changes | `OrderService` |

That is a strong SRP smell.

A better split might be:

```python
class OrderValidator:
    def validate(self, order):
        ...

class OrderRepository:
    def save(self, order):
        ...

class NotificationService:
    def notify_order_confirmed(self, order):
        ...

class AnalyticsTracker:
    def track_order_placed(self, order):
        ...

class OrderService:
    def __init__(self, validator, repository, notifier, analytics):
        self.validator = validator
        self.repository = repository
        self.notifier = notifier
        self.analytics = analytics

    def place_order(self, order):
        self.validator.validate(order)
        self.repository.save(order)
        self.notifier.notify_order_confirmed(order)
        self.analytics.track_order_placed(order)
```

Important nuance: `OrderService` can still coordinate the workflow. SRP does **not** mean `place_order()` can only call one thing. It means it should not personally own all the details.

---

## 2. Open/Closed Principle

This part is the obvious OCP violation:

```python
if order.customer.preferred_notification == "email":
    ...
elif order.customer.preferred_notification == "sms":
    ...
elif order.customer.preferred_notification == "push":
    ...
```

Every new notification channel requires editing `OrderService`.

For example, adding WhatsApp, Slack, or in-app messages means modifying existing code that already works.

A better approach would be to use a common interface:

```python
class NotificationChannel:
    def send_order_confirmation(self, order):
        raise NotImplementedError
```

Then implementations:

```python
class EmailNotificationChannel(NotificationChannel):
    def send_order_confirmation(self, order):
        self.email_sender.send(
            order.customer.email,
            "Order confirmed",
            "Thanks for your order!"
        )

class SmsNotificationChannel(NotificationChannel):
    def send_order_confirmation(self, order):
        self.sms_sender.send(
            order.customer.phone_number,
            "Thanks for your order!"
        )

class PushNotificationChannel(NotificationChannel):
    def send_order_confirmation(self, order):
        self.push_sender.send(
            order.customer.device_id,
            "Order confirmed"
        )
```

Then selection can happen elsewhere:

```python
class NotificationService:
    def __init__(self, channels):
        self.channels = channels

    def notify_order_confirmed(self, order):
        channel = self.channels[order.customer.preferred_notification]
        channel.send_order_confirmation(order)
```

Now adding WhatsApp means adding a new class and registering it, not editing `OrderService`.

---

## 3. Dependency Inversion Principle

This is the DIP smell:

```python
database = MySQLDatabase()
email_sender = EmailSender()
sms_sender = SmsSender()
push_sender = PushSender()
analytics = AnalyticsClient()
```

`OrderService` directly creates concrete low-level dependencies.

That makes it tightly coupled to:

```text
MySQL
EmailSender
SmsSender
PushSender
AnalyticsClient
```

Problems:

- It is harder to test because you cannot easily pass fake dependencies.
- It is harder to swap infrastructure because `OrderService` knows exactly which concrete classes to use.
- It makes the business flow depend on technical details.

A better version:

```python
class OrderService:
    def __init__(self, order_repository, notification_service, analytics_tracker, order_validator):
        self.order_repository = order_repository
        self.notification_service = notification_service
        self.analytics_tracker = analytics_tracker
        self.order_validator = order_validator

    def place_order(self, order):
        self.order_validator.validate(order)
        self.order_repository.save(order)
        self.notification_service.notify_order_confirmed(order)
        self.analytics_tracker.track_order_placed(order)
```

Now `OrderService` depends on abstractions: something that saves orders, something that sends notifications, and something that tracks analytics.

It does not care whether the database is MySQL, PostgreSQL, DynamoDB, or an in-memory fake.

---

## 4. Interface Segregation Principle

There is no explicit large interface here, so we cannot say it definitely violates ISP.

But there is a possible risk.

Suppose you created one big dependency like this:

```python
class OrderInfrastructure:
    def save(self, order):
        ...

    def send_email(self, ...):
        ...

    def send_sms(self, ...):
        ...

    def send_push(self, ...):
        ...

    def track(self, ...):
        ...
```

That would likely violate ISP because clients would depend on methods they do not use.

A better design would use smaller interfaces:

```python
class OrderRepository:
    def save(self, order):
        ...

class OrderNotifier:
    def notify_order_confirmed(self, order):
        ...

class OrderAnalytics:
    def track_order_placed(self, order):
        ...
```

So for this specific code, the critique is:

> No direct ISP violation is visible, but the fix should avoid creating one giant manager or infrastructure interface.

---

## 5. Liskov Substitution Principle

There is no inheritance or subtype relationship shown, so there is no direct LSP violation in the current code.

But LSP matters when you refactor.

For example, this could become problematic:

```python
class NotificationChannel:
    def send_order_confirmation(self, order):
        raise NotImplementedError

class SmsNotificationChannel(NotificationChannel):
    def send_order_confirmation(self, order):
        if not order.customer.phone_number:
            raise Exception("Cannot send SMS")
```

That may or may not violate LSP depending on the contract.

If the parent contract says "send the order confirmation," but some implementations fail for normal orders, callers now need to know implementation-specific details.

A better design might make eligibility explicit:

```python
class NotificationChannel:
    def can_send(self, order):
        raise NotImplementedError

    def send_order_confirmation(self, order):
        raise NotImplementedError
```

Or validate notification preferences before calling the channel.

So the critique is:

> No immediate LSP issue, but any notification abstraction should define a contract that all notification channels can honestly satisfy.

---

## Other Design Smells

### Hidden side effects

`place_order()` does several external things:

```text
writes to database
sends customer notification
tracks analytics
```

That makes the method harder to reason about. If notification sending fails, what happens to the order? Was it already saved? Should analytics still run?

The current design has unclear failure behavior.

Example questions:

- If database save succeeds but email fails, is the order placed?
- If analytics fails, should the order placement fail?
- Should notifications be retried?
- Should analytics be async?

---

### Transaction boundary is unclear

The order is saved before notifications and analytics.

```python
database.save(order)
# then send notification
# then track analytics
```

That might be okay, but the business rule should be clear.

Usually, saving the order is core. Notification and analytics are secondary side effects. Many systems would avoid failing the whole order just because analytics failed.

A more robust design may use events:

```python
class OrderService:
    def place_order(self, order):
        self.validator.validate(order)
        self.repository.save(order)
        self.events.publish(OrderPlaced(order))
```

Then separate handlers respond:

```python
class SendOrderConfirmation:
    def handle(self, event):
        ...

class TrackOrderPlacedAnalytics:
    def handle(self, event):
        ...
```

This can be clean when the system grows. For a small app, direct calls may be enough.

---

### The method knows too much about customer contact details

This code:

```python
order.customer.email
order.customer.phone_number
order.customer.device_id
```

means `OrderService` knows the data requirements for every notification type.

That is another reason notification logic should be moved elsewhere.

`OrderService` should probably say:

```python
self.notifier.notify_order_confirmed(order)
```

Not:

```python
if email, use email address
if sms, use phone number
if push, use device id
```

---

### Hard to test

With the current design, a unit test for order validation might accidentally touch:

```text
MySQLDatabase
EmailSender
SmsSender
PushSender
AnalyticsClient
```

That is a big testing smell.

A cleaner design lets you test the order flow with fakes:

```python
fake_repository = FakeOrderRepository()
fake_notifier = FakeNotifier()
fake_analytics = FakeAnalytics()
validator = OrderValidator()

service = OrderService(
    validator,
    fake_repository,
    fake_notifier,
    fake_analytics
)
```

Then you can assert:

```python
assert fake_repository.saved_order == order
assert fake_notifier.confirmed_order == order
assert fake_analytics.tracked_order == order
```

---

## Which Parts Are Okay?

The validation itself is not necessarily bad:

```python
if not order.items:
    raise ValueError("Order must contain at least one item")

if order.total <= 0:
    raise ValueError("Order total must be positive")
```

For a very small app, simple inline validation can be fine.

The workflow order is also understandable:

```text
validate order
save order
notify customer
track analytics
```

That sequence is clear.

The problem is not the existence of these steps. The problem is that `OrderService` owns all implementation details for every step.

---

## Summary

| Principle | Critique |
|---|---|
| SRP | Violated. `OrderService` validates, saves, notifies, tracks analytics, and creates dependencies. |
| OCP | Violated. Adding a new notification type requires editing `OrderService`. |
| DIP | Violated. `OrderService` directly creates `MySQLDatabase`, senders, and analytics client. |
| ISP | Not directly visible, but avoid replacing this with one giant interface. |
| LSP | Not directly visible because no inheritance or subtyping is shown. Be careful when introducing notification abstractions. |

The strongest issues are **SRP**, **OCP**, and **DIP**. The main extra critique points are failure behavior, testability, unclear transaction boundaries, and the fact that ISP/LSP are not obvious violations from this exact snippet.
