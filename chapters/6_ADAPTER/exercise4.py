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
    """TODO: Adapt a TemperatureSeries into TrainingWindows and cache the result."""

    _cache: ClassVar[dict[tuple[str, int, int, int], tuple[TrainingWindow, ...]]] = {}
    generation_count: ClassVar[int] = 0

    def __init__(self, series: TemperatureSeries, window_size: int, horizon: int = 1):
        # TODO: validate inputs.
        # TODO: create and store the cache key.
        # TODO: generate windows only if the key is missing.
        pass

    @classmethod
    def clear_cache(cls) -> None:
        # TODO: clear the cache and reset generation_count.
        raise NotImplementedError

    @staticmethod
    def _generate_windows(
        series: TemperatureSeries,
        window_size: int,
        horizon: int,
    ) -> tuple[TrainingWindow, ...]:
        # TODO: reuse the window-generation logic from Exercise 3.
        raise NotImplementedError

    def __iter__(self) -> Iterator[TrainingWindow]:
        # TODO: return an iterator over cached windows for this adapter's key.
        raise NotImplementedError

    def __len__(self) -> int:
        # TODO: return the number of cached windows for this adapter's key.
        raise NotImplementedError


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
