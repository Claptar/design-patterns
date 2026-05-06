---
layout: default
title: Adapter and Adapter Caching Exercises
---

# Adapter and Adapter Caching Exercises

This exercise pack uses one running example: greenhouse temperature data.

The client code wants clean `TemperatureReading` and `TrainingWindow` objects. The legacy system gives data in shapes that do not match that interface.

The parts gradually add complexity:

| Part | Topic | Main idea |
|---|---|---|
| 1 | Basic Adapter | Wrap one legacy reading so it looks like the target object. |
| 2 | One-to-many Adapter | Wrap one legacy batch and expose many normalized readings. |
| 3 | Derived-object Adapter | Convert a time series into many training windows. |
| 4 | Cached Adapter | Cache generated windows so repeated adaptation is not repeated. |

Each part contains:

- `exercise<part-num>.py` - skeleton and basic tests
- `exercise<part-num>.md` - exercise details
- `exercise_solution<part-num>.py` - complete solution
- `solution<part-num>.md` - explanation, pitfalls, and possible improvements

Run a solution file with:

```bash
python exercise_solution1.py
```

Run a skeleton file with:

```bash
python exercise1.py
```

The skeleton tests are expected to fail until the TODOs are implemented.
