from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class TemperatureReading:
    sensor_id: str
    timestamp: int
    celsius: float


def count_hot_readings(readings, threshold: float = 30.0) -> int:
    """Client code: expects an iterable of objects with a celsius attribute."""
    return sum(1 for reading in readings if reading.celsius >= threshold)


class LegacyBatch:
    """Legacy batch: one object containing many incompatible raw rows."""

    def __init__(self, device: str, rows: list[tuple[int, float | None]]):
        self._device = device
        self._rows = rows

    def device_id(self) -> str:
        return self._device

    def raw_rows(self) -> list[tuple[int, float | None]]:
        return self._rows


class LegacyBatchToReadingsAdapter:
    """TODO: Adapt one LegacyBatch into many TemperatureReading objects."""

    def __init__(self, batch: LegacyBatch):
        # TODO: build and store normalized TemperatureReading objects.
        pass

    def __iter__(self) -> Iterator[TemperatureReading]:
        # TODO: return an iterator over the normalized readings.
        raise NotImplementedError

    def __len__(self) -> int:
        # TODO: return the number of normalized readings.
        raise NotImplementedError


def run_tests() -> None:
    batch = LegacyBatch(
        device="greenhouse-1",
        rows=[
            (100, 68.0),
            (101, 86.0),
            (102, None),
            (103, 77.0),
        ],
    )

    adapter = LegacyBatchToReadingsAdapter(batch)
    readings = list(adapter)

    assert len(adapter) == 3
    assert readings == [
        TemperatureReading(sensor_id="greenhouse-1", timestamp=100, celsius=20.0),
        TemperatureReading(sensor_id="greenhouse-1", timestamp=101, celsius=30.0),
        TemperatureReading(sensor_id="greenhouse-1", timestamp=103, celsius=25.0),
    ]
    assert count_hot_readings(adapter) == 1

    empty_batch = LegacyBatch(device="greenhouse-2", rows=[(200, None)])
    empty_adapter = LegacyBatchToReadingsAdapter(empty_batch)

    assert len(empty_adapter) == 0
    assert list(empty_adapter) == []

    print("Exercise 2 tests passed")


if __name__ == "__main__":
    run_tests()
