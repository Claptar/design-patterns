---
layout: default
title: "Bridge Exercise 1: Building the Basic Shape"
---

# Bridge Exercise 1: Building the Basic Shape

## Goal

Practice the core Bridge mechanic: two separate hierarchies connected by a reference.

You will build a simple smart-home control system. Don't worry about realism — the goal is to get comfortable with the structural shape before applying it to harder problems.

---

## The domain

A smart-home app controls **devices** (a light, a fan). Devices can be operated at different **intensity levels** (low, high). The app sends commands, but the device decides how to carry them out.

The two dimensions are:

```
Devices:    Light, Fan
Intensity:  LowIntensity, HighIntensity
```

Without Bridge you'd end up with `LowIntensityLight`, `HighIntensityLight`, `LowIntensityFan`, `HighIntensityFan` — four classes for two dimensions, and it only gets worse from there.

---

## What you need to build

### Implementor interface: `Device`

```python
class Device(ABC):
    @abstractmethod
    def turn_on(self) -> None: ...

    @abstractmethod
    def turn_off(self) -> None: ...

    @abstractmethod
    def set_level(self, level: int) -> None:
        """Set the device's output level (0–100)."""
        ...

    @abstractmethod
    def status(self) -> str: ...
```

### Concrete implementors: `Light`, `Fan`

`Light.set_level(level)` should print something like `"Light brightness set to 75%"`.

`Fan.set_level(level)` should print something like `"Fan speed set to 40%"`.

Both should track whether they are on or off and their current level.

### Abstraction base: `RemoteControl`

```python
class RemoteControl(ABC):
    def __init__(self, device: Device):
        self._device = device   # <-- the bridge

    @abstractmethod
    def toggle_power(self) -> None: ...
```

### Refined abstractions: `LowIntensityRemote`, `HighIntensityRemote`

`LowIntensityRemote.toggle_power()` turns the device on at level 30, or off.

`HighIntensityRemote.toggle_power()` turns the device on at level 90, or off.

Both should track whether the device is currently on so they can toggle correctly.

---

## Expected output

```python
light = Light()
fan = Fan()

low_remote = LowIntensityRemote(light)
high_remote = HighIntensityRemote(fan)

low_remote.toggle_power()
# Light turned on
# Light brightness set to 30%

low_remote.toggle_power()
# Light turned off

high_remote.toggle_power()
# Fan turned on
# Fan speed set to 90%

print(light.status())  # Light: OFF, level=0
print(fan.status())    # Fan: ON, level=90
```

---

## Skeleton

See `exercise1.py`.

---

## Things to notice while you work

- `RemoteControl` never mentions `Light` or `Fan` by name. It only knows `Device`.
- `Light` and `Fan` never mention `LowIntensityRemote` or `HighIntensityRemote`. They only know their own job.
- You can freely combine any remote with any device at construction time.

---

[Exercise 2](exercise2.md)
