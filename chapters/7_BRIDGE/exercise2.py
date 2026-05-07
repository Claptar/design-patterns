"""
Bridge Exercise 2: The M×N Problem Appears

This file imports the solution from Exercise 1 as a starting point.
You only need to add the new classes below.

Parts:
  A  -- Add Thermostat and Speaker devices
  B  -- Add ScheduledRemote
  C  -- Verify all combinations in the tests at the bottom
"""

# Re-use everything from Exercise 1
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
        # TODO: set _on = True, print "Thermostat on"
        pass

    def turn_off(self) -> None:
        # TODO: set _on = False, _level = 0, print "Thermostat off"
        pass

    def set_level(self, level: int) -> None:
        # TODO: store level, print "Thermostat set to {level}°"
        pass

    def status(self) -> str:
        # TODO: return e.g. "Thermostat: ON, level=22"
        pass


class Speaker(Device):
    def __init__(self):
        self._on = False
        self._level = 0

    def turn_on(self) -> None:
        # TODO: set _on = True, print "Speaker on"
        pass

    def turn_off(self) -> None:
        # TODO: set _on = False, _level = 0, print "Speaker off"
        pass

    def set_level(self, level: int) -> None:
        # TODO: store level, print "Speaker volume set to {level}%"
        pass

    def status(self) -> str:
        # TODO: return e.g. "Speaker: ON, level=45"
        pass


# ---------------------------------------------------------------------------
# Part B: ScheduledRemote
# ---------------------------------------------------------------------------

class ScheduledRemote(RemoteControl):
    """
    Turns the device on at `level` for `duration_seconds`, then turns it off.
    Does not actually wait — just simulate by printing the schedule.
    """

    def __init__(self, device: Device, level: int, duration_seconds: int):
        super().__init__(device)
        # TODO: store level and duration_seconds
        pass

    def toggle_power(self) -> None:
        # TODO:
        #   1. turn the device on
        #   2. set the level
        #   3. print "[Scheduled] Will turn off after {n} seconds"
        #   4. turn the device off
        pass


# ---------------------------------------------------------------------------
# Tests — do not edit below this line
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    # Part A: new devices work with existing remotes
    print("=== Thermostat + LowIntensityRemote ===")
    t = Thermostat()
    r = LowIntensityRemote(t)
    r.toggle_power()
    assert t._on is True,   "Thermostat should be on"
    assert t._level == 30,  "Thermostat level should be 30"
    r.toggle_power()
    assert t._on is False,  "Thermostat should be off"

    print("\n=== Speaker + HighIntensityRemote ===")
    s = Speaker()
    r2 = HighIntensityRemote(s)
    r2.toggle_power()
    assert s._on is True,   "Speaker should be on"
    assert s._level == 90,  "Speaker level should be 90"
    print(s.status())
    assert "ON" in s.status()
    assert "90" in s.status()

    # Part B: ScheduledRemote works with any device
    print("\n=== ScheduledRemote + Speaker ===")
    s2 = Speaker()
    scheduled = ScheduledRemote(s2, level=60, duration_seconds=30)
    scheduled.toggle_power()
    assert s2._on is False,  "Device should be off after scheduled run"

    print("\n=== ScheduledRemote + Thermostat ===")
    t2 = Thermostat()
    scheduled2 = ScheduledRemote(t2, level=22, duration_seconds=3600)
    scheduled2.toggle_power()
    assert t2._on is False,  "Thermostat should be off after scheduled run"

    # Part C: original devices still work unchanged
    print("\n=== Original devices unaffected ===")
    light = Light()
    LowIntensityRemote(light).toggle_power()
    assert light._level == 30

    fan = Fan()
    ScheduledRemote(fan, level=50, duration_seconds=10).toggle_power()
    assert fan._on is False

    print("\nAll tests passed.")
