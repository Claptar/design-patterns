from __future__ import annotations
from abc import ABC, abstractmethod


class Metric(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def value(self) -> float: ...

    @abstractmethod
    def is_breaching(self) -> bool: ...

    @abstractmethod
    def to_dict(self) -> dict: ...

    @abstractmethod
    def display(self, indent: int = 0) -> None: ...


class MetricValue(Metric):
    def __init__(self, name: str, reading: float, unit: str = "",
                 threshold: float | None = None):
        super().__init__(name)
        self._reading = reading
        self._unit = unit
        # TODO: store threshold
        ...

    def value(self) -> float:
        return self._reading

    def is_breaching(self) -> bool:
        # TODO: True if threshold is set and value exceeds it
        ...

    def to_dict(self) -> dict:
        # TODO: return dict with name, value, unit, threshold, breaching
        ...

    def display(self, indent: int = 0) -> None:
        # TODO: prefix line with [!] when breaching; show threshold value
        ...


class MetricGroup(Metric):
    def __init__(self, name: str):
        super().__init__(name)
        self._children: list[Metric] = []

    def add(self, metric: Metric) -> "MetricGroup":
        self._children.append(metric)
        return self

    def value(self) -> float:
        if not self._children:
            raise ValueError(f"MetricGroup '{self.name}' has no children")
        return sum(child.value() for child in self._children) / len(self._children)

    def is_breaching(self) -> bool:
        # TODO: True if any child is_breaching()
        ...

    def to_dict(self) -> dict:
        # TODO: return dict with name, value, breaching, and children list
        ...

    def display(self, indent: int = 0) -> None:
        # TODO: show [!] prefix on group name when breaching;
        #       delegate display to each child
        ...


# ---------------------------------------------------------------------------
# Tests — do not modify
# ---------------------------------------------------------------------------

def test_breaching_leaf():
    m = MetricValue("cpu_usage", 92.0, "%", threshold=80.0)
    assert m.is_breaching() is True
    print("PASS test_breaching_leaf")


def test_not_breaching_leaf():
    m = MetricValue("cpu_usage", 73.2, "%", threshold=80.0)
    assert m.is_breaching() is False
    print("PASS test_not_breaching_leaf")


def test_no_threshold_never_breaching():
    m = MetricValue("cpu_usage", 99.9, "%")
    assert m.is_breaching() is False
    print("PASS test_no_threshold_never_breaching")


def test_group_breaching_if_any_child_breaches():
    g = MetricGroup("cpu")
    g.add(MetricValue("cpu_usage", 92.0, "%", threshold=80.0))
    g.add(MetricValue("cpu_iowait", 4.1, "%"))
    assert g.is_breaching() is True
    print("PASS test_group_breaching_if_any_child_breaches")


def test_group_not_breaching_when_all_fine():
    g = MetricGroup("cpu")
    g.add(MetricValue("cpu_usage", 50.0, "%", threshold=80.0))
    g.add(MetricValue("cpu_iowait", 4.1, "%"))
    assert g.is_breaching() is False
    print("PASS test_group_not_breaching_when_all_fine")


def test_to_dict_leaf():
    m = MetricValue("cpu_usage", 73.2, "%", threshold=80.0)
    d = m.to_dict()
    assert d["name"] == "cpu_usage"
    assert d["value"] == 73.2
    assert d["unit"] == "%"
    assert d["threshold"] == 80.0
    assert d["breaching"] is False
    print("PASS test_to_dict_leaf")


def test_to_dict_group():
    g = MetricGroup("cpu")
    g.add(MetricValue("cpu_usage", 92.0, "%", threshold=80.0))
    d = g.to_dict()
    assert d["name"] == "cpu"
    assert "children" in d
    assert len(d["children"]) == 1
    assert d["breaching"] is True
    print("PASS test_to_dict_group")


def test_to_dict_nested():
    system = MetricGroup("system")
    cpu = MetricGroup("cpu")
    cpu.add(MetricValue("cpu_usage", 92.0, "%", threshold=80.0))
    system.add(cpu)
    d = system.to_dict()
    assert d["children"][0]["name"] == "cpu"
    assert d["children"][0]["children"][0]["name"] == "cpu_usage"
    print("PASS test_to_dict_nested")


def test_display_shows_breach():
    system = MetricGroup("system")
    cpu = MetricGroup("cpu")
    cpu.add(MetricValue("cpu_usage", 92.0, "%", threshold=80.0))
    cpu.add(MetricValue("cpu_iowait", 4.1, "%"))
    system.add(cpu)
    print("--- display output ---")
    system.display()
    print("--- end ---")
    print("PASS test_display_shows_breach")


if __name__ == "__main__":
    test_breaching_leaf()
    test_not_breaching_leaf()
    test_no_threshold_never_breaching()
    test_group_breaching_if_any_child_breaches()
    test_group_not_breaching_when_all_fine()
    test_to_dict_leaf()
    test_to_dict_group()
    test_to_dict_nested()
    test_display_shows_breach()
