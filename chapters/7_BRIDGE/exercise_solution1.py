"""
Bridge Exercise 1: Solution
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
    def set_level(self, level: int) -> None: ...

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
        self._on = True
        print("Light turned on")

    def turn_off(self) -> None:
        self._on = False
        self._level = 0
        print("Light turned off")

    def set_level(self, level: int) -> None:
        self._level = level
        print(f"Light brightness set to {level}%")

    def status(self) -> str:
        state = "ON" if self._on else "OFF"
        return f"Light: {state}, level={self._level}"


class Fan(Device):
    def __init__(self):
        self._on = False
        self._level = 0

    def turn_on(self) -> None:
        self._on = True
        print("Fan turned on")

    def turn_off(self) -> None:
        self._on = False
        self._level = 0
        print("Fan turned off")

    def set_level(self, level: int) -> None:
        self._level = level
        print(f"Fan speed set to {level}%")

    def status(self) -> str:
        state = "ON" if self._on else "OFF"
        return f"Fan: {state}, level={self._level}"


# ---------------------------------------------------------------------------
# Abstraction base
# ---------------------------------------------------------------------------

class RemoteControl(ABC):
    def __init__(self, device: Device):
        self._device = device

    @abstractmethod
    def toggle_power(self) -> None: ...


# ---------------------------------------------------------------------------
# Refined abstractions
# ---------------------------------------------------------------------------

class LowIntensityRemote(RemoteControl):
    def __init__(self, device: Device):
        super().__init__(device)
        self._is_on = False

    def toggle_power(self) -> None:
        if self._is_on:
            self._device.turn_off()
        else:
            self._device.turn_on()
            self._device.set_level(30)
        self._is_on = not self._is_on


class HighIntensityRemote(RemoteControl):
    def __init__(self, device: Device):
        super().__init__(device)
        self._is_on = False

    def toggle_power(self) -> None:
        if self._is_on:
            self._device.turn_off()
        else:
            self._device.turn_on()
            self._device.set_level(90)
        self._is_on = not self._is_on


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Test 1: LowIntensityRemote + Light ===")
    light = Light()
    remote = LowIntensityRemote(light)

    remote.toggle_power()
    assert light._on is True
    assert light._level == 30

    remote.toggle_power()
    assert light._on is False
    assert light._level == 0

    print("=== Test 2: HighIntensityRemote + Fan ===")
    fan = Fan()
    remote2 = HighIntensityRemote(fan)

    remote2.toggle_power()
    assert fan._on is True
    assert fan._level == 90

    print("=== Test 3: status strings ===")
    assert "ON"  in fan.status()
    assert "90"  in fan.status()
    assert "OFF" in light.status()

    print("=== Test 4: any remote works with any device ===")
    fan2 = Fan()
    low_fan = LowIntensityRemote(fan2)
    low_fan.toggle_power()
    assert fan2._level == 30

    print("\nAll tests passed.")
