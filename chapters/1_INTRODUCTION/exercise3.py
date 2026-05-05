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
