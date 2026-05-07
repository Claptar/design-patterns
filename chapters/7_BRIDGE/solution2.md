---
layout: default
title: "Bridge Exercise 2: Solution & Discussion"
---

# Bridge Exercise 2: Solution & Discussion

## The solution

```python
class Thermostat(Device):
    def turn_on(self) -> None:
        self._on = True
        print("Thermostat on")

    def set_level(self, level: int) -> None:
        self._level = level
        print(f"Thermostat set to {level}°")

    def status(self) -> str:
        state = "ON" if self._on else "OFF"
        return f"Thermostat: {state}, level={self._level}"


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
```

---

## The M×N count before and after

| | Remotes | Devices | Classes needed |
|---|---|---|---|
| Without Bridge | 3 | 4 | 3 × 4 = **12** |
| With Bridge | 3 | 4 | 3 + 4 = **7** |

And more concretely, here is what you had to write in Exercise 2:

```
Added Thermostat   → 1 new class, 0 changes to existing remote classes
Added Speaker      → 1 new class, 0 changes to existing remote classes
Added ScheduledRemote → 1 new class, 0 changes to existing device classes
```

This is the payoff. Each addition is isolated. The two hierarchies are genuinely independent.

---

## Why `ScheduledRemote` doesn't need `toggle_power` state

In Exercise 1, both remotes tracked `self._is_on` because they needed to know whether to turn the device on or off when `toggle_power` is called again.

`ScheduledRemote` doesn't have that problem — it always runs a complete on-then-off cycle in a single call. There's no meaningful "already on" state to toggle. This is a natural consequence of the fact that the abstraction owns the high-level behavior, and different abstractions have genuinely different behaviors.

---

## A common question: who owns the "is on" state?

Notice that the device (`Light`, `Fan`, etc.) also tracks `self._on`, but the remote (`LowIntensityRemote`) tracks `self._is_on` separately.

Why both?

The device tracks its own hardware state — it knows what it was last told to do.
The remote tracks its own view of the situation — it knows what it last commanded.

In a real system these might drift apart (the device could be physically switched off while the remote still thinks it's on). Keeping them separate makes that possible to detect and handle. In this exercise they stay in sync, but the separation is still good design: each object owns the state that belongs to it.

---

## Pitfall: making `ScheduledRemote.toggle_power` too smart

A tempting mistake is to make `ScheduledRemote` check whether the device is currently on and behave differently:

```python
def toggle_power(self) -> None:
    if self._device._on:   # reaches into device internals
        self._device.turn_off()
    else:
        ...
```

This is wrong for two reasons:

1. It reaches into the device's private state (`_on`) rather than using the `Device` interface.
2. `ScheduledRemote`'s whole purpose is a timed on/off cycle — that's its contract. A conditional that sometimes skips the cycle breaks that contract.

If you find yourself reaching past the interface, that's a sign the interface may need an extension — or that you're asking the wrong object to make the decision.

---

## What we have now

```
RemoteControl ─────────────────► Device
      │                              │
      │                              │
LowIntensityRemote            Light
HighIntensityRemote           Fan
ScheduledRemote               Thermostat
                              Speaker
```

3 remotes + 4 devices = 7 classes. All 12 combinations work.

---

[Exercise 1](exercise1.md) · [Exercise 3](exercise3.md)
