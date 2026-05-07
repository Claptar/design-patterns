"""
Bridge Exercise 2: Solution
"""

from exercise_solution1 import (
    Device,
    RemoteControl,
    Light,
    Fan,
    LowIntensityRemote,
    HighIntensityRemote,
)


# ---------------------------------------------------------------------------
# Part A: New concrete implementors
# ---------------------------------------------------------------------------

class Thermostat(Device):
    def __init__(self):
        self._on = False
        self._level = 0

    def turn_on(self) -> None:
        self._on = True
        print("Thermostat on")

    def turn_off(self) -> None:
        self._on = False
        self._level = 0
        print("Thermostat off")

    def set_level(self, level: int) -> None:
        self._level = level
        print(f"Thermostat set to {level}°")

    def status(self) -> str:
        state = "ON" if self._on else "OFF"
        return f"Thermostat: {state}, level={self._level}"


class Speaker(Device):
    def __init__(self):
        self._on = False
        self._level = 0

    def turn_on(self) -> None:
        self._on = True
        print("Speaker on")

    def turn_off(self) -> None:
        self._on = False
        self._level = 0
        print("Speaker off")

    def set_level(self, level: int) -> None:
        self._level = level
        print(f"Speaker volume set to {level}%")

    def status(self) -> str:
        state = "ON" if self._on else "OFF"
        return f"Speaker: {state}, level={self._level}"


# ---------------------------------------------------------------------------
# Part B: ScheduledRemote
# ---------------------------------------------------------------------------

class ScheduledRemote(RemoteControl):
    def __init__(self, device: Device, level: int, duration_seconds: int):
        super().__init__(device)
        self._level = level
        self._duration = duration_seconds

    def toggle_power(self) -> None:
        self._device.turn_on()
        self._device.set_level(self._level)
        print(f"[Scheduled] Will turn off after {self._duration} seconds")
        self._device.turn_off()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    print("=== Thermostat + LowIntensityRemote ===")
    t = Thermostat()
    r = LowIntensityRemote(t)
    r.toggle_power()
    assert t._on is True
    assert t._level == 30
    r.toggle_power()
    assert t._on is False

    print("\n=== Speaker + HighIntensityRemote ===")
    s = Speaker()
    r2 = HighIntensityRemote(s)
    r2.toggle_power()
    assert s._on is True
    assert s._level == 90
    print(s.status())
    assert "ON" in s.status()
    assert "90" in s.status()

    print("\n=== ScheduledRemote + Speaker ===")
    s2 = Speaker()
    scheduled = ScheduledRemote(s2, level=60, duration_seconds=30)
    scheduled.toggle_power()
    assert s2._on is False

    print("\n=== ScheduledRemote + Thermostat ===")
    t2 = Thermostat()
    scheduled2 = ScheduledRemote(t2, level=22, duration_seconds=3600)
    scheduled2.toggle_power()
    assert t2._on is False

    print("\n=== Original devices unaffected ===")
    light = Light()
    LowIntensityRemote(light).toggle_power()
    assert light._level == 30

    fan = Fan()
    ScheduledRemote(fan, level=50, duration_seconds=10).toggle_power()
    assert fan._on is False

    print("\nAll tests passed.")
