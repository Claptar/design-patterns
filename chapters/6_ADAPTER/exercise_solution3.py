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
    """Adapt one TemperatureSeries into many TrainingWindow objects."""

    def __init__(self, series: TemperatureSeries, window_size: int, horizon: int = 1):
        if window_size <= 0:
            raise ValueError("window_size must be positive")
        if horizon <= 0:
            raise ValueError("horizon must be positive")

        windows: list[TrainingWindow] = []
        last_start = len(series.values) - window_size - horizon + 1

        for start in range(max(0, last_start)):
            features = tuple(series.values[start:start + window_size])
            target_index = start + window_size + horizon - 1
            target = series.values[target_index]
            windows.append(
                TrainingWindow(
                    sensor_id=series.sensor_id,
                    features=features,
                    target=target,
                )
            )

        self._windows = tuple(windows)

    def __iter__(self) -> Iterator[TrainingWindow]:
        return iter(self._windows)

    def __len__(self) -> int:
        return len(self._windows)


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
