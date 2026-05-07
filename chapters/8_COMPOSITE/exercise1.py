from abc import ABC, abstractmethod


class Metric(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def value(self) -> float: ...

    @abstractmethod
    def display(self, indent: int = 0) -> None: ...


class MetricValue(Metric):
    def __init__(self, name: str, reading: float, unit: str = ""):
        # TODO: call super().__init__ and store reading and unit
        ...

    def value(self) -> float:
        # TODO: return the stored reading
        ...

    def display(self, indent: int = 0) -> None:
        # TODO: print indented line like "    cpu_usage: 73.2 %"
        ...


class MetricGroup(Metric):
    def __init__(self, name: str):
        # TODO: call super().__init__ and initialise an empty children list
        ...

    def add(self, metric: Metric) -> "MetricGroup":
        # TODO: append metric to children and return self
        ...

    def value(self) -> float:
        # TODO: return mean of children values; raise ValueError if empty
        ...

    def display(self, indent: int = 0) -> None:
        # TODO: print group name with trailing "/", then display each child
        #       at indent + 2
        ...


# ---------------------------------------------------------------------------
# Tests — do not modify
# ---------------------------------------------------------------------------

def test_leaf_value():
    m = MetricValue("cpu_usage", 73.2, "%")
    assert m.value() == 73.2, f"Expected 73.2, got {m.value()}"
    print("PASS test_leaf_value")


def test_group_average():
    g = MetricGroup("cpu")
    g.add(MetricValue("cpu_usage", 80.0, "%"))
    g.add(MetricValue("cpu_iowait", 20.0, "%"))
    assert g.value() == 50.0, f"Expected 50.0, got {g.value()}"
    print("PASS test_group_average")


def test_nested_group_average():
    cpu = MetricGroup("cpu")
    cpu.add(MetricValue("cpu_usage", 60.0, "%"))
    cpu.add(MetricValue("cpu_iowait", 40.0, "%"))   # avg = 50.0

    mem = MetricGroup("memory")
    mem.add(MetricValue("mem_used", 70.0, "%"))     # avg = 70.0

    system = MetricGroup("system")
    system.add(cpu)
    system.add(mem)                                  # avg of (50, 70) = 60.0

    assert system.value() == 60.0, f"Expected 60.0, got {system.value()}"
    print("PASS test_nested_group_average")


def test_empty_group_raises():
    g = MetricGroup("empty")
    try:
        g.value()
        print("FAIL test_empty_group_raises — no exception raised")
    except ValueError:
        print("PASS test_empty_group_raises")


def test_uniform_interface():
    items: list[Metric] = [
        MetricValue("cpu_usage", 73.2, "%"),
        MetricGroup("memory"),
    ]
    items[1].add(MetricValue("mem_used", 61.0, "%"))

    for item in items:
        _ = item.value()
    print("PASS test_uniform_interface")


def test_display_runs():
    system = MetricGroup("system")
    cpu = MetricGroup("cpu")
    cpu.add(MetricValue("cpu_usage", 73.2, "%"))
    cpu.add(MetricValue("cpu_iowait", 4.1, "%"))
    system.add(cpu)
    system.add(MetricValue("requests_per_sec", 412.0, "req/s"))
    print("--- display output ---")
    system.display()
    print("--- end ---")
    print("PASS test_display_runs")


if __name__ == "__main__":
    test_leaf_value()
    test_group_average()
    test_nested_group_average()
    test_empty_group_raises()
    test_uniform_interface()
    test_display_runs()
