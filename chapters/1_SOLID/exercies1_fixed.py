from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping, Protocol


class OrderRepository(Protocol):
    def save(self, order: Any) -> None:
        ...


class OrderValidator:
    def validate(self, order: Any) -> None:
        if not order.items:
            raise ValueError("Order must contain at least one item")

        if order.total <= 0:
            raise ValueError("Order total must be positive")


class NotificationChannel(ABC):
    @abstractmethod
    def send_order_confirmation(self, order: Any) -> None:
        pass


class EmailOrderNotification(NotificationChannel):
    def __init__(self, email_sender: Any):
        self.email_sender = email_sender

    def send_order_confirmation(self, order: Any) -> None:
        self.email_sender.send(
            order.customer.email,
            "Order confirmed",
            "Thanks for your order!",
        )


class SmsOrderNotification(NotificationChannel):
    def __init__(self, sms_sender: Any):
        self.sms_sender = sms_sender

    def send_order_confirmation(self, order: Any) -> None:
        self.sms_sender.send(
            order.customer.phone_number,
            "Thanks for your order!",
        )


class PushOrderNotification(NotificationChannel):
    def __init__(self, push_sender: Any):
        self.push_sender = push_sender

    def send_order_confirmation(self, order: Any) -> None:
        self.push_sender.send(
            order.customer.device_id,
            "Order confirmed",
        )


class OrderNotifier:
    def __init__(self, channels: Mapping[str, NotificationChannel]):
        self.channels = channels

    def send_order_confirmation(self, order: Any) -> None:
        preferred_channel = order.customer.preferred_notification

        try:
            channel = self.channels[preferred_channel]
        except KeyError as exc:
            raise ValueError(f"Unsupported notification channel: {preferred_channel}") from exc

        channel.send_order_confirmation(order)


class OrderAnalytics(Protocol):
    def track_order_placed(self, order: Any) -> None:
        ...


class AnalyticsOrderTracker:
    def __init__(self, analytics_client: Any):
        self.analytics_client = analytics_client

    def track_order_placed(self, order: Any) -> None:
        self.analytics_client.track(
            "order_placed",
            {
                "order_id": order.id,
                "total": order.total,
                "customer_id": order.customer.id,
            },
        )


@dataclass
class OrderService:
    validator: OrderValidator
    repository: OrderRepository
    notifier: OrderNotifier
    analytics: OrderAnalytics

    def place_order(self, order: Any) -> None:
        self.validator.validate(order)
        self.repository.save(order)
        self.notifier.send_order_confirmation(order)
        self.analytics.track_order_placed(order)
