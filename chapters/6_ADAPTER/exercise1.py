from dataclasses import dataclass


@dataclass(frozen=True)
class TemperatureReading:
    sensor_id: str
    timestamp: int
    celsius: float


def alert_if_hot(reading: TemperatureReading) -> bool:
    """Client code: expects sensor_id, timestamp, and celsius attributes."""
    return reading.celsius >= 30.0


class LegacyReading:
    """Legacy object: useful data, incompatible interface."""

    def __init__(self, device: str, when: int, fahrenheit: float):
        self._device = device
        self._when = when
        self._fahrenheit = fahrenheit

    def device_id(self) -> str:
        return self._device

    def recorded_at(self) -> int:
        return self._when

    def temp_f(self) -> float:
        return self._fahrenheit


class LegacyReadingAdapter:
    """TODO: Adapt LegacyReading to the TemperatureReading-like interface."""

    def __init__(self, legacy_reading: LegacyReading):
        # TODO: store the wrapped legacy object.
        pass

    @property
    def sensor_id(self) -> str:
        # TODO: delegate to legacy_reading.device_id().
        raise NotImplementedError

    @property
    def timestamp(self) -> int:
        # TODO: delegate to legacy_reading.recorded_at().
        raise NotImplementedError

    @property
    def celsius(self) -> float:
        # TODO: convert legacy_reading.temp_f() from Fahrenheit to Celsius.
        raise NotImplementedError


def run_tests() -> None:
    legacy = LegacyReading(device="greenhouse-1", when=100, fahrenheit=86.0)
    adapted = LegacyReadingAdapter(legacy)

    assert adapted.sensor_id == "greenhouse-1"
    assert adapted.timestamp == 100
    assert adapted.celsius == 30.0
    assert alert_if_hot(adapted) is True

    cooler = LegacyReading(device="greenhouse-2", when=101, fahrenheit=68.0)
    cooler_adapted = LegacyReadingAdapter(cooler)

    assert cooler_adapted.celsius == 20.0
    assert alert_if_hot(cooler_adapted) is False

    print("Exercise 1 tests passed")


if __name__ == "__main__":
    run_tests()
