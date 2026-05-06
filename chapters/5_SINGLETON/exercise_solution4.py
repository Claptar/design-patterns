class Monostate:
    """Base class for objects that share state per subclass."""

    _shared_states = {}

    def __init__(self):
        cls = type(self)
        if cls not in self._shared_states:
            self._shared_states[cls] = {}
        self.__dict__ = self._shared_states[cls]

    @classmethod
    def reset_state(cls):
        Monostate._shared_states.pop(cls, None)


class Preferences(Monostate):
    def __init__(self, theme="light", language="en"):
        super().__init__()

        if getattr(self, "_initialized", False):
            return

        self.theme = theme
        self.language = language
        self._initialized = True


class Metrics(Monostate):
    def __init__(self):
        super().__init__()

        if getattr(self, "_initialized", False):
            return

        self.events = []
        self._initialized = True

    def record(self, event):
        self.events.append(event)


# Tests

def test_monostate_creates_different_objects():
    Preferences.reset_state()

    first = Preferences(theme="light")
    second = Preferences(theme="dark")

    assert first is not second


def test_preferences_share_the_same_state_dictionary():
    Preferences.reset_state()

    first = Preferences(theme="light")
    second = Preferences(theme="dark")

    assert first.__dict__ is second.__dict__


def test_attribute_change_is_visible_through_another_instance():
    Preferences.reset_state()

    first = Preferences(theme="light")
    second = Preferences(theme="dark")

    first.theme = "dark"

    assert second.theme == "dark"


def test_first_initialization_wins_for_preferences():
    Preferences.reset_state()

    first = Preferences(theme="light", language="en")
    second = Preferences(theme="dark", language="fr")

    assert first.theme == "light"
    assert second.theme == "light"
    assert second.language == "en"


def test_subclasses_have_separate_shared_state():
    Preferences.reset_state()
    Metrics.reset_state()

    preferences1 = Preferences(theme="dark")
    preferences2 = Preferences()

    metrics1 = Metrics()
    metrics2 = Metrics()
    metrics1.record("order-created")

    assert preferences1.__dict__ is preferences2.__dict__
    assert metrics1.__dict__ is metrics2.__dict__
    assert preferences1.__dict__ is not metrics1.__dict__
    assert metrics2.events == ["order-created"]
    assert not hasattr(metrics2, "theme")


def test_reset_state_creates_fresh_state_for_next_objects():
    Preferences.reset_state()

    old = Preferences(theme="dark")
    old.language = "fr"

    Preferences.reset_state()
    new = Preferences(theme="light", language="en")

    assert old.__dict__ is not new.__dict__
    assert new.theme == "light"
    assert new.language == "en"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__]))
