# SOLID Principles Guide

SOLID is a set of five object-oriented design principles that help make code easier to change, test, and understand.

The five principles are:

| Letter | Principle | Core idea |
|---|---|---|
| S | Single Responsibility Principle | One clear reason to change |
| O | Open/Closed Principle | Add new behavior without rewriting old code |
| L | Liskov Substitution Principle | Subclasses should safely replace their parents |
| I | Interface Segregation Principle | Prefer small, focused interfaces |
| D | Dependency Inversion Principle | Depend on abstractions, not concrete details |

---

## 1. Single Responsibility Principle

### Summary

The **Single Responsibility Principle** says:

> A class, function, or module should have one main reason to change.

In simpler words:

> Each piece of code should have one clear job.

This does **not** mean every class must have only one method. It means the class should have one coherent purpose.

---

### Bad example

```python
class Invoice:
    def calculate_total(self):
        ...

    def save_to_database(self):
        ...

    def print_invoice(self):
        ...
```

This class has multiple responsibilities:

1. Calculating invoice totals
2. Saving invoices
3. Printing invoices

That means it has multiple reasons to change:

- Tax rules change
- Database storage changes
- Invoice layout changes

Those are different responsibilities mixed together.

---

### Better example

```python
class Invoice:
    def calculate_total(self):
        ...


class InvoiceRepository:
    def save(self, invoice):
        ...


class InvoicePrinter:
    def print(self, invoice):
        ...
```

Now each class has a clearer purpose:

| Class | Responsibility |
|---|---|
| `Invoice` | Invoice business logic |
| `InvoiceRepository` | Saving invoices |
| `InvoicePrinter` | Printing invoices |

If the database changes, update `InvoiceRepository`.

If the print layout changes, update `InvoicePrinter`.

If the invoice calculation changes, update `Invoice`.

---

### When to use SRP

Use SRP when:

- A class or function is getting long and hard to understand
- A class name contains words like `And`, `Manager`, or `Handler` because it does too much
- A file imports unrelated things like database, email, PDF rendering, and payment code
- Changing one feature risks breaking another unrelated feature
- Tests are hard to write because the class touches too many systems

---

### When SRP is too much

Do not split code into tiny pieces just for the sake of splitting.

This may be unnecessary:

```python
class FirstNameValidator:
    ...

class LastNameValidator:
    ...

class EmailValidator:
    ...

class PasswordValidator:
    ...
```

A single validator may be clearer:

```python
class UserValidator:
    def validate(self, user_data):
        ...
```

SRP is about **cohesion**, not making every class microscopic.

---

## 2. Open/Closed Principle

### Summary

The **Open/Closed Principle** says:

> Software should be open for extension, but closed for modification.

In simpler words:

> You should be able to add new behavior without constantly editing old, working code.

---

### Bad example

```python
def calculate_discount(customer_type, price):
    if customer_type == "regular":
        return price * 0.95
    elif customer_type == "vip":
        return price * 0.80
    elif customer_type == "employee":
        return price * 0.50
```

Every time you add a new customer type, you have to modify this function:

```python
elif customer_type == "student":
    return price * 0.90
```

That can become risky as the function grows.

---

### Better example

```python
class RegularDiscount:
    def apply(self, price):
        return price * 0.95


class VipDiscount:
    def apply(self, price):
        return price * 0.80


class EmployeeDiscount:
    def apply(self, price):
        return price * 0.50


def calculate_discount(discount_strategy, price):
    return discount_strategy.apply(price)
```

Now you can add a new discount without changing `calculate_discount`:

```python
class StudentDiscount:
    def apply(self, price):
        return price * 0.90
```

The system is open to new discount types, but the existing calculator does not need to change.

---

### When to use OCP

Use OCP when you have several versions of the same kind of behavior and expect more later.

Good examples:

| Area | Possible variations |
|---|---|
| Payments | Card, PayPal, Apple Pay, bank transfer |
| Notifications | Email, SMS, push, Slack |
| Exporting | PDF, CSV, JSON, XML |
| Discounts | Regular, VIP, student, seasonal |
| Authentication | Google, GitHub, SAML, email/password |

It is especially useful when you keep seeing code like this:

```python
if type == "A":
    ...
elif type == "B":
    ...
elif type == "C":
    ...
```

and you know more types are likely to appear.

---

### When OCP is too much

Do not create abstractions for every tiny condition.

This is probably fine:

```python
if user.is_logged_in:
    show_account()
else:
    show_login()
```

This would probably be over-engineered:

```python
class LoggedInPageRenderer:
    ...

class LoggedOutPageRenderer:
    ...

class PageRendererFactory:
    ...
```

OCP is useful when change is expected. It is not useful when you are protecting against imaginary future complexity.

---

## 3. Liskov Substitution Principle

### Summary

The **Liskov Substitution Principle** says:

> If a child class inherits from a parent class, the child should be usable anywhere the parent is expected.

In simpler words:

> A subclass should not break the promises made by its parent class.

---

### Bad example

```python
class Bird:
    def fly(self):
        print("Flying")


class Sparrow(Bird):
    def fly(self):
        print("Sparrow flying")


class Penguin(Bird):
    def fly(self):
        raise Exception("Penguins cannot fly")
```

This breaks LSP because code that expects a `Bird` might reasonably call `fly()`:

```python
def make_bird_fly(bird):
    bird.fly()
```

This works:

```python
make_bird_fly(Sparrow())
```

But this breaks:

```python
make_bird_fly(Penguin())
```

The problem is not that penguins are not birds in real life. The problem is that this `Bird` class promises flying behavior.

A `Penguin` cannot safely substitute for that kind of `Bird`.

---

### Better example

```python
class Bird:
    pass


class FlyingBird(Bird):
    def fly(self):
        print("Flying")


class Sparrow(FlyingBird):
    def fly(self):
        print("Sparrow flying")


class Penguin(Bird):
    pass
```

Now only birds that can actually fly inherit from `FlyingBird`.

```python
def make_bird_fly(bird: FlyingBird):
    bird.fly()
```

A penguin is still a bird, but it is not treated as a flying bird.

---

### Classic rectangle and square example

Mathematically, a square is a rectangle. But in code, inheritance can still be wrong.

```python
class Rectangle:
    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def area(self):
        return self.width * self.height
```

Now imagine this:

```python
class Square(Rectangle):
    def set_width(self, width):
        self.width = width
        self.height = width

    def set_height(self, height):
        self.width = height
        self.height = height
```

This can break code that expects a normal rectangle:

```python
def resize_rectangle(rectangle):
    rectangle.set_width(10)
    rectangle.set_height(5)
    return rectangle.area()
```

For a rectangle, the result should be `50`.

For a square, the result becomes `25` because setting the height also changes the width.

So `Square` is not safely substitutable for this mutable `Rectangle` class.

---

### Better shape design

```python
class Shape:
    def area(self):
        raise NotImplementedError


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side * self.side
```

Both are shapes. One does not need to pretend to be the other.

---

### When to use LSP

Think about LSP whenever you use inheritance.

Ask:

> Can this child class be used anywhere the parent class is expected without surprising behavior?

Warning signs include:

- A subclass throws `NotImplementedError`
- A subclass ignores a method from the parent
- A subclass accepts fewer valid inputs than the parent
- A subclass returns results in a surprising format
- A subclass changes side effects that parent users depend on

---

### When LSP is too much

LSP mostly matters when you are using inheritance or polymorphism.

If you are not creating parent-child relationships, you usually do not need to think deeply about it.

The practical advice is simple:

> Do not use inheritance just because something sounds like an “is-a” relationship. Use inheritance only when the child honors the full behavior of the parent.

---

## 4. Interface Segregation Principle

### Summary

The **Interface Segregation Principle** says:

> Code should not be forced to depend on methods it does not use.

In simpler words:

> Prefer small, focused interfaces over large “do everything” interfaces.

---

### Bad example

```python
class Machine:
    def print_document(self, document):
        ...

    def scan_document(self, document):
        ...

    def fax_document(self, document):
        ...
```

This works for an all-in-one office machine.

But a basic printer cannot scan or fax:

```python
class BasicPrinter(Machine):
    def print_document(self, document):
        print("Printing")

    def scan_document(self, document):
        raise NotImplementedError()

    def fax_document(self, document):
        raise NotImplementedError()
```

This violates ISP because `BasicPrinter` is forced to implement methods it does not support.

---

### Better example

```python
class Printer:
    def print_document(self, document):
        ...


class Scanner:
    def scan_document(self, document):
        ...


class FaxMachine:
    def fax_document(self, document):
        ...
```

Now each device only implements the abilities it actually has:

```python
class BasicPrinter(Printer):
    def print_document(self, document):
        print("Printing")


class AllInOneMachine(Printer, Scanner, FaxMachine):
    def print_document(self, document):
        print("Printing")

    def scan_document(self, document):
        print("Scanning")

    def fax_document(self, document):
        print("Faxing")
```

---

### Client-focused example

Suppose this function only needs to print:

```python
def print_report(printer):
    printer.print_document("report")
```

It should depend on a `Printer`, not a huge `Machine` that also scans and faxes.

The function does not care about scanning or faxing. It only needs printing.

---

### When to use ISP

Use ISP when:

- Classes have methods that raise `NotImplementedError`
- Classes have empty methods only to satisfy an interface
- A function depends on a large object but only uses one or two methods
- Adding one method to an interface forces many unrelated classes to change
- Tests need large mocks full of irrelevant methods

---

### When ISP is too much

Do not split every method into its own interface.

This may be excessive:

```python
class CanGetName:
    def get_name(self):
        ...


class CanGetEmail:
    def get_email(self):
        ...


class CanGetAge:
    def get_age(self):
        ...
```

A simple `User` interface may be clearer.

The goal is not “one method per interface.”

The goal is:

> Keep interfaces grouped by what clients actually need.

---

## 5. Dependency Inversion Principle

### Summary

The **Dependency Inversion Principle** says:

> High-level code should not depend directly on low-level details. Both should depend on abstractions.

In simpler words:

> Your important business logic should not be tightly glued to databases, APIs, email providers, file systems, or frameworks.

---

### Bad example

```python
class MySQLDatabase:
    def save_user(self, user):
        print("Saving user to MySQL")


class UserService:
    def __init__(self):
        self.database = MySQLDatabase()

    def register_user(self, user):
        self.database.save_user(user)
```

`UserService` is high-level business logic.

`MySQLDatabase` is a low-level technical detail.

The problem is that `UserService` directly creates and depends on `MySQLDatabase`.

If you switch databases, or want a fake database for tests, you have to modify `UserService`.

---

### Better example

```python
class UserRepository:
    def save_user(self, user):
        raise NotImplementedError


class MySQLUserRepository(UserRepository):
    def save_user(self, user):
        print("Saving user to MySQL")


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register_user(self, user):
        self.repository.save_user(user)
```

Usage:

```python
repository = MySQLUserRepository()
service = UserService(repository)

service.register_user(user)
```

Now `UserService` does not know or care whether users are saved in MySQL, PostgreSQL, MongoDB, or a fake test repository.

It only knows:

> I need something that can save a user.

---

### Dependency inversion vs dependency injection

These are related, but not the same.

| Concept | Meaning |
|---|---|
| Dependency Inversion Principle | Depend on abstractions, not concrete details |
| Dependency Injection | Pass dependencies in from the outside |

This is dependency injection:

```python
class OrderService:
    def __init__(self, email_sender):
        self.email_sender = email_sender
```

This is the opposite:

```python
class OrderService:
    def __init__(self):
        self.email_sender = SendGridEmailSender()
```

Dependency injection is one common way to follow the Dependency Inversion Principle.

---

### Another example: email sender

Bad:

```python
class SendGridEmailSender:
    def send(self, to, subject, body):
        print("Sending email with SendGrid")


class OrderService:
    def __init__(self):
        self.email_sender = SendGridEmailSender()

    def place_order(self, order):
        self.email_sender.send(
            order.customer_email,
            "Order confirmed",
            "Thanks for your order"
        )
```

Better:

```python
class EmailSender:
    def send(self, to, subject, body):
        raise NotImplementedError


class SendGridEmailSender(EmailSender):
    def send(self, to, subject, body):
        print("Sending email with SendGrid")


class FakeEmailSender(EmailSender):
    def __init__(self):
        self.sent_messages = []

    def send(self, to, subject, body):
        self.sent_messages.append((to, subject, body))


class OrderService:
    def __init__(self, email_sender: EmailSender):
        self.email_sender = email_sender

    def place_order(self, order):
        self.email_sender.send(
            order.customer_email,
            "Order confirmed",
            "Thanks for your order"
        )
```

Now production code can use `SendGridEmailSender`, while tests can use `FakeEmailSender`.

---

### When to use DIP

Use DIP when your core code talks to things that are:

- External
- Slow
- Changeable
- Hard to test
- Side-effect-heavy
- Framework-specific

Examples:

| Dependency | Why abstraction helps |
|---|---|
| Database | Easier to swap and test |
| Email provider | Easier to change vendors |
| Payment gateway | Easier to support multiple providers |
| File system | Easier to test without real files |
| External API | Easier to mock failures |
| Message queue | Easier to isolate business logic |

---

### When DIP is too much

Do not abstract every tiny operation.

This is overkill:

```python
class AdditionProvider:
    def add(self, a, b):
        return a + b


class Calculator:
    def __init__(self, addition_provider):
        self.addition_provider = addition_provider
```

This is enough:

```python
result = a + b
```

DIP is most useful for dependencies that are external, unstable, slow, or hard to test.

---

# How the Principles Work Together

The SOLID principles often overlap.

Here is one combined example.

```python
class EmailSender:
    def send(self, to, subject, body):
        raise NotImplementedError


class SendGridEmailSender(EmailSender):
    def send(self, to, subject, body):
        print("Sending email with SendGrid")


class MailgunEmailSender(EmailSender):
    def send(self, to, subject, body):
        print("Sending email with Mailgun")


class FakeEmailSender(EmailSender):
    def __init__(self):
        self.sent_messages = []

    def send(self, to, subject, body):
        self.sent_messages.append((to, subject, body))


class OrderService:
    def __init__(self, email_sender: EmailSender):
        self.email_sender = email_sender

    def place_order(self, order):
        # order business logic would go here
        self.email_sender.send(
            order.customer_email,
            "Order confirmed",
            "Thanks for your order"
        )
```

This uses multiple SOLID principles:

| Principle | How it appears here |
|---|---|
| SRP | `OrderService` handles orders; email senders handle sending email |
| OCP | Add a new email provider without changing `OrderService` |
| LSP | `SendGridEmailSender`, `MailgunEmailSender`, and `FakeEmailSender` can all replace `EmailSender` |
| ISP | `EmailSender` only exposes the `send` method that clients need |
| DIP | `OrderService` depends on `EmailSender`, not directly on SendGrid or Mailgun |

---

# Quick Comparison

| Principle | Main question | Common smell | Typical fix |
|---|---|---|---|
| SRP | Does this have one reason to change? | Class does too many unrelated things | Split responsibilities |
| OCP | Can I add behavior without changing old code? | Long `if/elif` or `switch` chains | Use polymorphism, strategies, plugins |
| LSP | Can the child replace the parent safely? | Subclass breaks parent expectations | Fix inheritance or use composition/interfaces |
| ISP | Is this interface too large? | Classes implement fake or unused methods | Split into smaller interfaces |
| DIP | Does core logic depend on details? | Service creates concrete database/API/email objects | Depend on abstractions and inject dependencies |

---

# Practical Checklist

Use this when reviewing code.

## SRP checklist

Ask:

> Does this class or function have one clear job?

Warning signs:

- It mixes business logic and database code
- It mixes formatting and calculation
- It sends emails, saves data, validates input, and tracks analytics all in one place

---

## OCP checklist

Ask:

> When I add a new case, do I keep editing the same old function?

Warning signs:

- Growing `if/elif` chains
- Repeated modifications to stable code
- Many variations of the same behavior

---

## LSP checklist

Ask:

> Can this subclass be used anywhere the parent is expected?

Warning signs:

- Subclass throws `NotImplementedError`
- Subclass disables parent behavior
- Subclass has surprising restrictions

---

## ISP checklist

Ask:

> Does every implementer genuinely need every method in this interface?

Warning signs:

- Empty methods
- Fake implementations
- Big interfaces used only partially

---

## DIP checklist

Ask:

> Is my important business logic directly tied to a concrete tool?

Warning signs:

- `UserService` creates `MySQLDatabase()` directly
- `OrderService` creates `SendGridEmailSender()` directly
- Tests require real databases, real APIs, or real file systems

---

# Final Mental Model

## SRP

> Do one job.

## OCP

> Add new behavior without rewriting old behavior.

## LSP

> Children should keep their parents' promises.

## ISP

> Do not force code to depend on abilities it does not use.

## DIP

> Keep core logic independent from concrete tools.

---

# Best Overall Rule

Do not apply SOLID mechanically.

Use these principles when they make code easier to change, test, and understand.

A simple `if` statement is not automatically bad.

A small class is not automatically good.

An abstraction is useful only when it reduces real complexity instead of adding imaginary complexity.

The goal is not to make code look “architectural.”

The goal is to make future changes safer and easier.

---

# Exercise: Report Exporting

Files:

- [Original implementation](exercise2.py)
- [Fixed implementation](exercise2_fixed.py)

## Scenario

```python
class ReportService:
    def export_report(self, report, export_type, user):
        # Check permissions
        if user.role != "admin" and not user.can_export_reports:
            raise PermissionError("User cannot export reports")

        # Prepare report data
        rows = []
        for item in report.items:
            rows.append({
                "name": item.name,
                "amount": item.amount,
                "date": item.date.strftime("%Y-%m-%d")
            })

        # Export report
        if export_type == "csv":
            content = "name,amount,date\n"
            for row in rows:
                content += f"{row['name']},{row['amount']},{row['date']}\n"

            file_name = report.title + ".csv"
            file_type = "text/csv"

        elif export_type == "json":
            import json
            content = json.dumps(rows)

            file_name = report.title + ".json"
            file_type = "application/json"

        elif export_type == "html":
            content = "<table>"
            for row in rows:
                content += (
                    f"<tr>"
                    f"<td>{row['name']}</td>"
                    f"<td>{row['amount']}</td>"
                    f"<td>{row['date']}</td>"
                    f"</tr>"
                )
            content += "</table>"

            file_name = report.title + ".html"
            file_type = "text/html"

        else:
            raise ValueError("Unsupported export type")

        audit_logger = AuditLogger()
        audit_logger.log({
            "event": "report_exported",
            "report_id": report.id,
            "user_id": user.id,
            "export_type": export_type
        })

        storage = S3Storage()
        url = storage.upload(file_name, content, file_type)

        return url
```

## Summary critique

| Principle | Critique |
|---|---|
| SRP | Violated. The service handles permissions, mapping, exporting, auditing, uploading, and dependency creation. |
| OCP | Violated. New export types require editing `ReportService`. |
| DIP | Violated. The service directly creates `AuditLogger` and `S3Storage`. |
| ISP | Not directly visible. Be careful not to introduce one giant interface during refactoring. |
| LSP | Not directly visible. Matters once exporter abstractions are introduced. |

The fixed implementation is intentionally kept in a separate file: [exercise2_fixed.py](exercise2_fixed.py)
