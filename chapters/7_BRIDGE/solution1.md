---
layout: default
title: "Bridge Exercise 1: Solution & Discussion"
---

# Bridge Exercise 1: Solution & Discussion

## The solution

```python
class Light(Device):
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


class RemoteControl(ABC):
    def __init__(self, device: Device):
        self._device = device   # <-- the bridge


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
```

---

## What to notice

### The bridge is just a constructor argument

```python
low_remote = LowIntensityRemote(light)
high_remote = HighIntensityRemote(fan)
```

The two hierarchies only meet at construction. After that they are completely decoupled. `LowIntensityRemote` never imports `Light`. `Light` never imports `RemoteControl`. Each side only knows about the shared interface (`Device` and `RemoteControl`).

### `self._device` is typed as `Device`, not `Light`

This is the key discipline. If you wrote:

```python
def __init__(self, device: Light):
    self._device = device
```

you'd break the bridge. The remote would only work with lights, and you'd be back to the M×N problem. The whole point is that the abstraction refers to the *interface*, not the concrete class.

### The toggle state lives on the remote, not the device

`self._is_on` tracks power state on the remote side. This is intentional — the remote controls the device, and the remote is responsible for knowing what it last told the device to do. The device just executes commands; it doesn't tell the remote what state it thinks it's in.

This is a small example of the broader principle: let each side own the state that belongs to it.

---

## Common mistakes

**Importing the concrete device class into the remote.**
This defeats the pattern. The remote should only know about `Device`.

**Calling `set_level` before `turn_on`.**
The order matters for the output to read naturally. Turn on first, then set the level — that's the logical sequence a physical device would follow.

**Forgetting to reset `_level` to 0 in `turn_off`.**
The status method becomes misleading if the device reports `OFF, level=90`. When a device turns off, its effective level is zero.

---

## What we have now

```
RemoteControl ──────────► Device
      │                      │
      │                      │
LowIntensityRemote      Light
HighIntensityRemote     Fan
```

2 remotes + 2 devices = 4 classes total.
Without Bridge: 2 × 2 = 4 classes — same count here, but see Exercise 2 for why this matters.

---

[Exercise 2](exercise2.md)
