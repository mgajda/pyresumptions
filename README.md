pyResumptions
=============

This project is a remake of my tools for debugging long running parallel computations.

It provides decorators for your functions, that allow you store *resumptions*
of the computation to be executed later, or ran as a unit test.

Examples:
---------

The `@resumable()` decorator allows you to see resumption upon each exception raised by the function:

```python3
@resumable()
def someFunction(args):
  raise NotImplementedError
```
After executing this code you will see call to the `someFunction(...)` with all argument values indicated.

The `@checkpoint()` decorator allows you to see resumption upon each execution of this function.

It is recommended that if data objects that you pass to any `@resumable`/`@checkpoint` function
are either:
* base types
* are descendants of a `Storable` class
* implement `store(self, variableName)` method that either:
  - writes the data in a convenient format, and returns code string that reads this data,
  - stores the data as a Python code.

For details, on what are arguments and results of `store()` method, please look at the function source code.
I plan to add documentation in the future.

