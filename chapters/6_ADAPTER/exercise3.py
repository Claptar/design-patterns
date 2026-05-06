from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class TemperatureSeries:
    sensor_id: str
    version: int
    values: tuple[float, ...]


@dataclass(frozen=True)
class TrainingWindow:
    sensor_id: str
    features: tuple[float, ...]
    target: float


def average_target(windows) -> float:
    """Client code: expects an iterable of TrainingWindow objects."""
    windows = list(windows)
    if not windows:
        return 0.0
    return sum(window.target for window in windows) / len(windows)


class SeriesToWindowAdapter:
    """TODO: Adapt one TemperatureSeries into many TrainingWindow objects."""

    def __init__(self, series: TemperatureSeries, window_size: int, horizon: int = 1):
        # TODO: validate inputs and generate windows.
        pass

    def __iter__(self) -> Iterator[TrainingWindow]:
        # TODO: return an iterator over generated windows.
        raise NotImplementedError

    def __len__(self) -> int:
        # TODO: return the number of generated windows.
        raise NotImplementedError


def assert_raises(expected_error, func) -> None:
    try:
        func()
    except expected_error:
        return
    raise AssertionError(f"Expected {expected_error.__name__}")


def run_tests() -> None:
    series = TemperatureSeries(
        sensor_id="greenhouse-1",
        version=1,
        values=(20.0, 21.0, 22.0, 23.0, 24.0),
    )

    adapter = SeriesToWindowAdapter(series, window_size=3)
    windows = list(adapter)

    assert len(adapter) == 2
    assert windows == [
        TrainingWindow(sensor_id="greenhouse-1", features=(20.0, 21.0, 22.0), target=23.0),
        TrainingWindow(sensor_id="greenhouse-1", features=(21.0, 22.0, 23.0), target=24.0),
    ]
    assert average_target(adapter) == 23.5

    horizon_adapter = SeriesToWindowAdapter(series, window_size=2, horizon=2)
    assert list(horizon_adapter) == [
        TrainingWindow(sensor_id="greenhouse-1", features=(20.0, 21.0), target=23.0),
        TrainingWindow(sensor_id="greenhouse-1", features=(21.0, 22.0), target=24.0),
    ]

    short_series = TemperatureSeries(sensor_id="greenhouse-2", version=1, values=(20.0, 21.0))
    assert list(SeriesToWindowAdapter(short_series, window_size=3)) == []

    assert_raises(ValueError, lambda: SeriesToWindowAdapter(series, window_size=0))
    assert_raises(ValueError, lambda: SeriesToWindowAdapter(series, window_size=2, horizon=0))

    print("Exercise 3 tests passed")


if __name__ == "__main__":
    run_tests()
