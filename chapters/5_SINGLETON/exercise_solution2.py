def singleton(cls):
    """Return a callable that creates cls once and then reuses it."""

    instance = None

    def get_instance(*args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = cls(*args, **kwargs)
        return instance

    def reset_instance():
        nonlocal instance
        instance = None

    # These helpers make the decorated class easier to inspect and reset in exercises.
    get_instance.reset_instance = reset_instance
    get_instance.__wrapped__ = cls
    return get_instance


@singleton
class MetricsRegistry:
    def __init__(self, namespace="default"):
        self.namespace = namespace
        self.counters = {}

    def increment(self, name):
        self.counters[name] = self.counters.get(name, 0) + 1

    def get(self, name):
        return self.counters.get(name, 0)


@singleton
class AuditLog:
    def __init__(self):
        self.events = []

    def record(self, event):
        self.events.append(event)


# Tests

def test_decorator_returns_same_metrics_registry_object():
    MetricsRegistry.reset_instance()

    billing_metrics = MetricsRegistry(namespace="billing")
    email_metrics = MetricsRegistry(namespace="email")

    assert billing_metrics is email_metrics
    assert email_metrics.namespace == "billing"


def test_state_is_shared_through_decorated_singleton():
    MetricsRegistry.reset_instance()

    first = MetricsRegistry(namespace="billing")
    second = MetricsRegistry(namespace="email")

    first.increment("payments_failed")

    assert second.get("payments_failed") == 1


def test_reset_instance_creates_a_fresh_object_next_time():
    MetricsRegistry.reset_instance()

    first = MetricsRegistry(namespace="billing")
    first.increment("orders_created")

    MetricsRegistry.reset_instance()
    second = MetricsRegistry(namespace="email")

    assert first is not second
    assert second.namespace == "email"
    assert second.get("orders_created") == 0


def test_each_decorated_class_has_its_own_cached_instance():
    MetricsRegistry.reset_instance()
    AuditLog.reset_instance()

    metrics = MetricsRegistry(namespace="billing")
    log = AuditLog()
    log.record("started")

    assert metrics is not log
    assert AuditLog().events == ["started"]


def test_original_class_is_available_through_wrapped():
    assert MetricsRegistry.__wrapped__.__name__ == "MetricsRegistry"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__]))
