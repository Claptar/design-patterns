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
