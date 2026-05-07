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

    @abstractmethod
    def find(self, name: str) -> "Metric | None": ...

    @abstractmethod
    def all_breaching(self) -> "list[Metric]": ...

    @abstractmethod
    def leaves(self) -> "list[MetricValue]": ...


class MetricValue(Metric):
    def __init__(self, name: str, reading: float, unit: str = "",
                 threshold: float | None = None):
        super().__init__(name)
        self._reading = reading
        self._unit = unit
        self._threshold = threshold

    def value(self) -> float:
        return self._reading

    def is_breaching(self) -> bool:
        return self._threshold is not None and self._reading > self._threshold

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self._reading,
            "unit": self._unit,
            "threshold": self._threshold,
            "breaching": self.is_breaching(),
        }

    def display(self, indent: int = 0) -> None:
        prefix = "[!] " if self.is_breaching() else ""
        unit_str = f" {self._unit}" if self._unit else ""
        threshold_str = (
            f"  (threshold: {self._threshold})" if self.is_breaching() else ""
        )
        print(" " * indent + f"{prefix}{self.name}: {self._reading}{unit_str}{threshold_str}")

    def find(self, name: str) -> "Metric | None":
        # TODO: return self if self.name == name, else None
        ...

    def all_breaching(self) -> "list[Metric]":
        # TODO: return [self] if is_breaching(), else []
        ...

    def leaves(self) -> "list[MetricValue]":
        # TODO: return [self]
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
        return any(child.is_breaching() for child in self._children)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value(),
            "breaching": self.is_breaching(),
            "children": [child.to_dict() for child in self._children],
        }

    def display(self, indent: int = 0) -> None:
        prefix = "[!] " if self.is_breaching() else ""
        print(" " * indent + f"{prefix}{self.name}/")
        for child in self._children:
            child.display(indent + 2)

    def find(self, name: str) -> "Metric | None":
        # TODO: return self if name matches; otherwise search children
        #       depth-first and return first match, or None
        ...

    def all_breaching(self) -> "list[Metric]":
        # TODO: collect breaching nodes from all children recursively
        ...

    def leaves(self) -> "list[MetricValue]":
        # TODO: concatenate child.leaves() for each child
        ...


# ---------------------------------------------------------------------------
# Tests — do not modify
# ---------------------------------------------------------------------------

def _build_tree() -> MetricGroup:
    cpu = MetricGroup("cpu")
    cpu.add(MetricValue("cpu_usage", 92.0, "%", threshold=80.0))
    cpu.add(MetricValue("cpu_iowait", 4.1, "%"))

    mem = MetricGroup("memory")
    mem.add(MetricValue("mem_used", 61.0, "%", threshold=90.0))

    system = MetricGroup("system")
    system.add(cpu)
    system.add(mem)
    return system


def test_find_leaf_by_name():
    system = _build_tree()
    result = system.find("cpu_usage")
    assert result is not None
    assert result.name == "cpu_usage"
    print("PASS test_find_leaf_by_name")


def test_find_group_by_name():
    system = _build_tree()
    result = system.find("cpu")
    assert result is not None
    assert result.name == "cpu"
    print("PASS test_find_group_by_name")


def test_find_returns_none_for_missing():
    system = _build_tree()
    result = system.find("does_not_exist")
    assert result is None
    print("PASS test_find_returns_none_for_missing")


def test_find_on_leaf_self_match():
    m = MetricValue("cpu_usage", 73.2, "%")
    assert m.find("cpu_usage") is m
    print("PASS test_find_on_leaf_self_match")


def test_find_on_leaf_no_match():
    m = MetricValue("cpu_usage", 73.2, "%")
    assert m.find("other") is None
    print("PASS test_find_on_leaf_no_match")


def test_all_breaching_finds_leaves():
    system = _build_tree()
    breaching = system.all_breaching()
    names = [m.name for m in breaching]
    assert "cpu_usage" in names
    print("PASS test_all_breaching_finds_leaves")


def test_all_breaching_empty_when_none_breach():
    g = MetricGroup("cpu")
    g.add(MetricValue("cpu_usage", 50.0, "%", threshold=80.0))
    result = g.all_breaching()
    leaf_names = [m.name for m in result if isinstance(m, MetricValue)]
    assert "cpu_usage" not in leaf_names
    print("PASS test_all_breaching_empty_when_none_breach")


def test_leaves_returns_all_leaf_nodes():
    system = _build_tree()
    leaf_names = {m.name for m in system.leaves()}
    assert "cpu_usage" in leaf_names
    assert "cpu_iowait" in leaf_names
    assert "mem_used" in leaf_names
    assert "system" not in leaf_names
    assert "cpu" not in leaf_names
    print("PASS test_leaves_returns_all_leaf_nodes")


def test_leaves_on_leaf_returns_self():
    m = MetricValue("cpu_usage", 73.2, "%")
    assert m.leaves() == [m]
    print("PASS test_leaves_on_leaf_returns_self")


if __name__ == "__main__":
    test_find_leaf_by_name()
    test_find_group_by_name()
    test_find_returns_none_for_missing()
    test_find_on_leaf_self_match()
    test_find_on_leaf_no_match()
    test_all_breaching_finds_leaves()
    test_all_breaching_empty_when_none_breach()
    test_leaves_returns_all_leaf_nodes()
    test_leaves_on_leaf_returns_self()
