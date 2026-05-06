from dataclasses import dataclass
from typing import ClassVar, Iterator


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


class CachedSeriesToWindowAdapter:
    """Adapt a TemperatureSeries into TrainingWindows and cache the result."""

    _cache: ClassVar[dict[tuple[str, int, int, int], tuple[TrainingWindow, ...]]] = {}
    generation_count: ClassVar[int] = 0

    def __init__(self, series: TemperatureSeries, window_size: int, horizon: int = 1):
        if window_size <= 0:
            raise ValueError("window_size must be positive")
        if horizon <= 0:
            raise ValueError("horizon must be positive")

        self._key = (series.sensor_id, series.version, window_size, horizon)

        if self._key not in type(self)._cache:
            type(self).generation_count += 1
            type(self)._cache[self._key] = self._generate_windows(
                series=series,
                window_size=window_size,
                horizon=horizon,
            )

    @classmethod
    def clear_cache(cls) -> None:
        cls._cache.clear()
        cls.generation_count = 0

    @staticmethod
    def _generate_windows(
        series: TemperatureSeries,
        window_size: int,
        horizon: int,
    ) -> tuple[TrainingWindow, ...]:
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

        return tuple(windows)

    def __iter__(self) -> Iterator[TrainingWindow]:
        return iter(type(self)._cache[self._key])

    def __len__(self) -> int:
        return len(type(self)._cache[self._key])


def assert_raises(expected_error, func) -> None:
    try:
        func()
    except expected_error:
        return
    raise AssertionError(f"Expected {expected_error.__name__}")


def run_tests() -> None:
    CachedSeriesToWindowAdapter.clear_cache()

    series_v1 = TemperatureSeries(
        sensor_id="greenhouse-1",
        version=1,
        values=(20.0, 21.0, 22.0, 23.0, 24.0),
    )

    adapter1 = CachedSeriesToWindowAdapter(series_v1, window_size=3)
    adapter2 = CachedSeriesToWindowAdapter(series_v1, window_size=3)

    assert CachedSeriesToWindowAdapter.generation_count == 1
    assert list(adapter1) == list(adapter2)
    assert len(adapter1) == 2

    different_window_size = CachedSeriesToWindowAdapter(series_v1, window_size=2)
    assert CachedSeriesToWindowAdapter.generation_count == 2
    assert len(different_window_size) == 3

    series_v2 = TemperatureSeries(
        sensor_id="greenhouse-1",
        version=2,
        values=(30.0, 31.0, 32.0, 33.0, 34.0),
    )

    updated = CachedSeriesToWindowAdapter(series_v2, window_size=3)
    assert CachedSeriesToWindowAdapter.generation_count == 3
    assert list(updated)[0] == TrainingWindow(
        sensor_id="greenhouse-1",
        features=(30.0, 31.0, 32.0),
        target=33.0,
    )

    same_updated = CachedSeriesToWindowAdapter(series_v2, window_size=3)
    assert CachedSeriesToWindowAdapter.generation_count == 3
    assert list(same_updated) == list(updated)

    assert_raises(ValueError, lambda: CachedSeriesToWindowAdapter(series_v1, window_size=0))
    assert_raises(ValueError, lambda: CachedSeriesToWindowAdapter(series_v1, window_size=2, horizon=0))

    print("Exercise 4 tests passed")


if __name__ == "__main__":
    run_tests()
