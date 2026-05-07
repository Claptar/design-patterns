---
layout: default
title: "Bridge Exercise 2: The M×N Problem Appears"
---

# Bridge Exercise 2: The M×N Problem Appears

## What changed since Exercise 1

The smart-home app is growing. Two things happened:

**New devices were added:** `Thermostat` and `Speaker`.

**New remote behaviors were added:** alongside low and high intensity, there is now a `ScheduledRemote` that turns a device on at a given level for a set duration, then turns it off automatically.

If you hadn't used Bridge in Exercise 1, your class list would now look like this:

```
LowIntensityLight
HighIntensityLight
ScheduledLight

LowIntensityFan
HighIntensityFan
ScheduledFan

LowIntensityThermostat
HighIntensityThermostat
ScheduledThermostat

LowIntensitySpeaker
HighIntensitySpeaker
ScheduledSpeaker
```

That's 12 classes for 3 remotes × 4 devices — and you'd write most of the same logic over and over.

With Bridge, you need to add:

```
Thermostat    (1 new class)
Speaker       (1 new class)
ScheduledRemote  (1 new class)
```

Three new classes total. Every combination works automatically.

---

## Part A — Add the new devices

Extend the system from Exercise 1 with two new concrete implementors.

### `Thermostat`

`set_level(level)` interprets the level as a target temperature in degrees. Level 30 means 30°C, level 90 means 90°F... keep it simple, just store and print the value.

Print: `"Thermostat set to {level}°"` when `set_level` is called.
Print: `"Thermostat on"` / `"Thermostat off"` for power.
`status()` returns e.g. `"Thermostat: ON, level=22"`.

### `Speaker`

`set_level(level)` controls volume.

Print: `"Speaker volume set to {level}%"` when `set_level` is called.
Print: `"Speaker on"` / `"Speaker off"` for power.
`status()` returns e.g. `"Speaker: ON, level=45"`.

---

## Part B — Add `ScheduledRemote`

`ScheduledRemote` takes a device, a level, and a duration in seconds. When `toggle_power()` is called:

1. It turns the device on at the given level.
2. It prints how long the device will stay on.
3. It does **not** actually wait (no `time.sleep` — just simulate by printing).
4. It then immediately turns the device off and prints a confirmation.

```python
class ScheduledRemote(RemoteControl):
    def __init__(self, device: Device, level: int, duration_seconds: int):
        ...
```

Expected output for `ScheduledRemote(speaker, level=60, duration_seconds=30).toggle_power()`:

```
Speaker on
Speaker volume set to 60%
[Scheduled] Will turn off after 30 seconds
Speaker off
```

---

## Part C — Verify all combinations work

After implementing Parts A and B, all nine combinations should work without any changes to the existing remote classes:

```python
devices  = [Light(), Fan(), Thermostat(), Speaker()]
remotes  = [LowIntensityRemote, HighIntensityRemote]

for DeviceClass in [Thermostat, Speaker]:
    device = DeviceClass()
    r = LowIntensityRemote(device)
    r.toggle_power()
    print(device.status())
    r.toggle_power()
```

And:

```python
speaker = Speaker()
scheduled = ScheduledRemote(speaker, level=60, duration_seconds=30)
scheduled.toggle_power()
```

---

## Skeleton

See `exercise2.py`. It imports everything from `exercise_solution1.py` so you only need to add the new classes.

---

## Things to think about

- When you add `Thermostat`, do you need to touch `LowIntensityRemote` at all?
- When you add `ScheduledRemote`, do you need to touch `Light` or `Fan` at all?
- That independence is exactly what Bridge is buying you.

---

[Exercise 1](exercise1.md) · [Exercise 3](exercise3.md)
