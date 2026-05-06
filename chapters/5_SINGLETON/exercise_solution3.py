class RegularSettings:
    """This class uses the regular metaclass: type."""

    def __init__(self, environment):
        self.environment = environment


class SingletonMeta(type):
    """Metaclass that should cache one instance per class."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    def reset_instance(cls):
        cls._instances.pop(cls, None)


class Settings(metaclass=SingletonMeta):
    def __init__(self, environment):
        self.environment = environment
        self.initialization_count = getattr(self, "initialization_count", 0) + 1


class PluginRegistry(metaclass=SingletonMeta):
    def __init__(self):
        self.plugins = {}

    def register(self, name, plugin):
        self.plugins[name] = plugin

    def get(self, name):
        return self.plugins[name]


# Tests

def test_regular_class_creates_new_objects_each_time():
    first = RegularSettings("development")
    second = RegularSettings("production")

    assert first is not second
    assert first.environment == "development"
    assert second.environment == "production"


def test_singleton_meta_returns_same_object_for_same_class():
    Settings.reset_instance()

    first = Settings("development")
    second = Settings("production")

    assert first is second
    assert second.environment == "development"


def test_init_runs_only_once_for_singleton_meta():
    Settings.reset_instance()

    first = Settings("development")
    second = Settings("production")

    assert first.initialization_count == 1
    assert second.initialization_count == 1


def test_class_identity_is_preserved():
    Settings.reset_instance()

    settings = Settings("development")

    assert isinstance(settings, Settings)


def test_each_singleton_class_has_its_own_cached_instance():
    Settings.reset_instance()
    PluginRegistry.reset_instance()

    settings = Settings("development")
    registry1 = PluginRegistry()
    registry2 = PluginRegistry()

    registry1.register("csv", object())

    assert registry1 is registry2
    assert settings is not registry1
    assert registry2.get("csv") is registry1.get("csv")


def test_reset_instance_removes_only_one_class_from_cache():
    Settings.reset_instance()
    PluginRegistry.reset_instance()

    old_settings = Settings("development")
    registry = PluginRegistry()
    registry.register("json", object())

    Settings.reset_instance()
    new_settings = Settings("test")

    assert old_settings is not new_settings
    assert new_settings.environment == "test"
    assert PluginRegistry().get("json") is registry.get("json")


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__]))
