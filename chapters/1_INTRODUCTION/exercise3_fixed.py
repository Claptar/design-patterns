from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Protocol


@dataclass
class Invoice:
    id: str
    customer_id: str
    plan_name: str
    amount: Decimal
    status: str = "pending"
    charge_id: Optional[str] = None


class BillingValidator(Protocol):
    def validate(self, customer, plan, amount: Decimal) -> None:
        ...


class PriceCalculator(Protocol):
    def calculate(self, customer, plan, usage) -> Decimal:
        ...


class PaymentProcessor(Protocol):
    def charge(self, payment_method, amount: Decimal) -> str:
        ...


class InvoiceRepository(Protocol):
    def create_pending_invoice(self, customer, plan, amount: Decimal) -> Invoice:
        ...

    def mark_paid(self, invoice_id: str, charge_id: Optional[str]) -> None:
        ...

    def mark_failed(self, invoice_id: str) -> None:
        ...


class ReceiptSender(Protocol):
    def send_receipt(self, customer, invoice: Invoice) -> None:
        ...


class DefaultBillingValidator:
    def validate(self, customer, plan, amount: Decimal) -> None:
        if not customer.is_active:
            raise ValueError("Inactive customers cannot be billed")

        # Free invoices should not necessarily require a payment method.
        if amount > Decimal("0") and customer.payment_method is None:
            raise ValueError("Customer has no payment method")


class DefaultPriceCalculator:
    PLAN_PRICES = {
        "free": Decimal("0"),
        "starter": Decimal("19"),
        "pro": Decimal("49"),
        "enterprise": Decimal("499"),
    }

    def calculate(self, customer, plan, usage) -> Decimal:
        try:
            amount = self.PLAN_PRICES[plan.name]
        except KeyError as exc:
            raise ValueError("Unknown plan") from exc

        if usage.api_calls > plan.included_api_calls:
            extra_calls = usage.api_calls - plan.included_api_calls
            amount += Decimal(extra_calls) * Decimal("0.01")

        if usage.storage_gb > plan.included_storage_gb:
            extra_storage = usage.storage_gb - plan.included_storage_gb
            amount += Decimal(extra_storage) * Decimal("0.25")

        if customer.is_nonprofit:
            amount *= Decimal("0.8")

        if customer.has_annual_contract:
            amount *= Decimal("0.9")

        if customer.coupon_code == "WELCOME10":
            amount *= Decimal("0.9")

        return amount.quantize(Decimal("0.01"))


class BillingService:
    def __init__(
        self,
        validator: BillingValidator,
        price_calculator: PriceCalculator,
        payment_processors: dict[str, PaymentProcessor],
        invoice_repository: InvoiceRepository,
        receipt_sender: ReceiptSender,
    ):
        self.validator = validator
        self.price_calculator = price_calculator
        self.payment_processors = payment_processors
        self.invoice_repository = invoice_repository
        self.receipt_sender = receipt_sender

    def bill_customer(self, customer, plan, usage) -> Optional[str]:
        amount = self.price_calculator.calculate(customer, plan, usage)
        self.validator.validate(customer, plan, amount)

        invoice = self.invoice_repository.create_pending_invoice(
            customer=customer,
            plan=plan,
            amount=amount,
        )

        if amount == Decimal("0"):
            self.invoice_repository.mark_paid(invoice.id, charge_id=None)
            self.receipt_sender.send_receipt(customer, invoice)
            return None

        try:
            processor = self.payment_processors[customer.payment_provider]
        except KeyError as exc:
            self.invoice_repository.mark_failed(invoice.id)
            raise ValueError("Unsupported payment provider") from exc

        try:
            charge_id = processor.charge(customer.payment_method, amount)
            self.invoice_repository.mark_paid(invoice.id, charge_id)
            invoice.charge_id = charge_id
            invoice.status = "paid"
            self.receipt_sender.send_receipt(customer, invoice)
            return charge_id
        except Exception:
            self.invoice_repository.mark_failed(invoice.id)
            raise
