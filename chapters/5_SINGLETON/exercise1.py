class AppSettings:
    """Application settings should have exactly one shared instance."""

    _instance = None

    def __new__(cls, environment="development", debug=False):
        # TODO: Create the instance only once.
        # Later calls should return the already-created object.
        return super().__new__(cls)

    def __init__(self, environment="development", debug=False):
        # TODO: Guard initialization so it runs only once.
        # Without this, every AppSettings(...) call will reset shared state.
        self.environment = environment
        self.debug = debug
        self.features = {}

    def enable_feature(self, name):
        self.features[name] = True

    def disable_feature(self, name):
        self.features[name] = False

    def is_enabled(self, name):
        return self.features.get(name, False)


# Test helpers

def reset_app_settings():
    AppSettings._instance = None


# Tests

def test_two_calls_return_the_same_object():
    reset_app_settings()

    first = AppSettings(environment="development", debug=False)
    second = AppSettings(environment="production", debug=True)

    assert first is second


def test_first_initialization_wins():
    reset_app_settings()

    first = AppSettings(environment="development", debug=False)
    second = AppSettings(environment="production", debug=True)

    assert second.environment == "development"
    assert second.debug is False


def test_state_is_shared_between_references():
    reset_app_settings()

    first = AppSettings()
    second = AppSettings()

    first.enable_feature("new-dashboard")

    assert second.is_enabled("new-dashboard") is True


def test_later_calls_do_not_reset_features():
    reset_app_settings()

    settings = AppSettings()
    settings.enable_feature("beta-checkout")

    same_settings = AppSettings(environment="production", debug=True)

    assert same_settings.is_enabled("beta-checkout") is True
    assert same_settings.environment == "development"
    assert same_settings.debug is False


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__]))
