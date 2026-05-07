"""
Bridge Exercise 1: Building the Basic Shape

Fill in every place marked TODO.
Run the file when you are done — the assertions at the bottom will tell you
whether your implementation is correct.
"""

from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# Implementor interface
# ---------------------------------------------------------------------------

class Device(ABC):
    @abstractmethod
    def turn_on(self) -> None: ...

    @abstractmethod
    def turn_off(self) -> None: ...

    @abstractmethod
    def set_level(self, level: int) -> None:
        """Set output level 0-100."""
        ...

    @abstractmethod
    def status(self) -> str: ...


# ---------------------------------------------------------------------------
# Concrete implementors
# ---------------------------------------------------------------------------

class Light(Device):
    def __init__(self):
        self._on = False
        self._level = 0

    def turn_on(self) -> None:
        # TODO: set self._on = True and print "Light turned on"
        pass

    def turn_off(self) -> None:
        # TODO: set self._on = False, self._level = 0, print "Light turned off"
        pass

    def set_level(self, level: int) -> None:
        # TODO: store the level and print e.g. "Light brightness set to 75%"
        pass

    def status(self) -> str:
        # TODO: return e.g. "Light: ON, level=75" or "Light: OFF, level=0"
        pass


class Fan(Device):
    def __init__(self):
        self._on = False
        self._level = 0

    def turn_on(self) -> None:
        # TODO: set self._on = True and print "Fan turned on"
        pass

    def turn_off(self) -> None:
        # TODO: set self._on = False, self._level = 0, print "Fan turned off"
        pass

    def set_level(self, level: int) -> None:
        # TODO: store the level and print e.g. "Fan speed set to 40%"
        pass

    def status(self) -> str:
        # TODO: return e.g. "Fan: ON, level=90" or "Fan: OFF, level=0"
        pass


# ---------------------------------------------------------------------------
# Abstraction base
# ---------------------------------------------------------------------------

class RemoteControl(ABC):
    def __init__(self, device: Device):
        # TODO: store the device as self._device (this is the bridge)
        pass

    @abstractmethod
    def toggle_power(self) -> None: ...


# ---------------------------------------------------------------------------
# Refined abstractions
# ---------------------------------------------------------------------------

class LowIntensityRemote(RemoteControl):
    """Turns the device on at level 30, or off if already on."""

    def __init__(self, device: Device):
        super().__init__(device)
        # TODO: track whether the device is currently on (self._is_on = False)
        pass

    def toggle_power(self) -> None:
        # TODO: if off -> turn on at level 30, flip _is_on
        #        if on  -> turn off, flip _is_on
        pass


class HighIntensityRemote(RemoteControl):
    """Turns the device on at level 90, or off if already on."""

    def __init__(self, device: Device):
        super().__init__(device)
        # TODO: track whether the device is currently on (self._is_on = False)
        pass

    def toggle_power(self) -> None:
        # TODO: if off -> turn on at level 90, flip _is_on
        #        if on  -> turn off, flip _is_on
        pass


# ---------------------------------------------------------------------------
# Tests — do not edit below this line
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Test 1: LowIntensityRemote + Light ===")
    light = Light()
    remote = LowIntensityRemote(light)

    remote.toggle_power()
    assert light._on is True,  "Light should be on after first toggle"
    assert light._level == 30, "Light level should be 30"

    remote.toggle_power()
    assert light._on is False, "Light should be off after second toggle"
    assert light._level == 0,  "Light level should reset to 0 when off"

    print("=== Test 2: HighIntensityRemote + Fan ===")
    fan = Fan()
    remote2 = HighIntensityRemote(fan)

    remote2.toggle_power()
    assert fan._on is True,   "Fan should be on after first toggle"
    assert fan._level == 90,  "Fan level should be 90"

    print("=== Test 3: status strings ===")
    assert "ON"  in fan.status(),   "status() should mention ON"
    assert "90"  in fan.status(),   "status() should mention 90"
    assert "OFF" in light.status(), "status() should mention OFF"

    print("=== Test 4: any remote works with any device ===")
    fan2 = Fan()
    low_fan = LowIntensityRemote(fan2)
    low_fan.toggle_power()
    assert fan2._level == 30, "LowIntensityRemote should work with Fan too"

    print("\nAll tests passed.")
