# Singleton Pattern Exercises

This pack contains four gradual exercises about shared-instance and shared-state patterns in Python.

The running example is application runtime state:

1. `AppSettings` starts as one shared settings object.
2. The singleton logic becomes reusable with a decorator.
3. The same idea is implemented with a metaclass, while preserving normal class identity.
4. Monostate changes the problem: many objects are allowed, but their state is shared.

Each part contains four files:

- `exerciseN.py` - skeleton code with basic tests
- `exerciseN.md` - exercise instructions
- `exercise_solutionN.py` - complete solution code with tests
- `solutionN.md` - explanation, discussion, and pitfalls

## How to use

Open one exercise at a time. Fill the TODOs in `exerciseN.py`, then run:

```bash
python -m pytest exerciseN.py
```

To check the provided solution:

```bash
python -m pytest exercise_solutionN.py
```
