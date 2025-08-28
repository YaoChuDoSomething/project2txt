# GEMINI.md

# Strengthened System Prompt 

**Goal:** Generate Python code that strictly follows Google Style docstrings and full PEP 8 compliance. All outputs must be ready to pass `flake8`, `pydocstyle` (Google convention), and `isort` (import ordering).

## Global Requirements

* **Type hints:** Use complete Python type annotations for all public and private callables, variables with non-trivial types, and class attributes.  
* **Module docstring:** Each file starts with a one-paragraph summary, usage note, and `Raises`/`Exceptions` summary if relevant.  
* **Logging:** Use the standard `logging` library (no `print`) for operational messages. Provide a module-level logger via `logging.getLogger(__name__)`.  
* **Errors:** Prefer specific exception types. Document every raised exception in docstrings’ **Raises**.  
* **Immutability & safety:** Use `dataclasses.dataclass(frozen=True)` when objects are value-like; otherwise document mutability.  
* **Dependency boundaries:** Keep I/O (filesystem, network) in thin adapters; inject dependencies via parameters or constructor.

## Documentation Requirements (Google Style)

For **every** function, method, class, and module:

* **Summary line**: One sentence, ends with a period.  
* **Args:** Use `name (type): description`. Indicate units where applicable.  
* **Returns:** `type: description`. Use `None` if no value is returned.  
* **Raises:** List all possible exceptions and when they occur.  
* **Examples:** Include when non-trivial; keep runnable and minimal.  
* **Attributes (for classes):** Document public attributes in an **Attributes** section.  
* **Property methods:** Document behavior, units, and side effects.  
* **Formatting:** Triple double quotes `"""` and consistent indentation.

## PEP 8 Compliance

* **Line length:** max 79 for code; max 72 for docstrings/comments.  
* **Naming:** `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants, `_private` prefix for internal use.  
* **Indentation:** 4 spaces, no tabs.  
* **Imports:** Group as 1\) standard library, 2\) third-party, 3\) local; blank line between groups; avoid unused imports; absolute imports preferred.  
* **Spacing:** Two blank lines before top-level defs/classes; one blank line between class methods; proper operator/comma spacing.  
* **Strings:** Be consistent with quotes within a file (choose single or double and stick to it).

## Testing & Tooling

* Provide at least one **doctest**\-style or `pytest` example for non-trivial functions.  
    
* Code must be compatible with Python **3.11+** (unless specified otherwise).  
    
* Output must pass:  
    
  * `flake8` (E/W conventions),  
  * `pydocstyle` (Google docstring rules),  
  * `isort` (import order).


* If randomness or time is used, make it deterministic (seed or injectable clock) in examples/tests.

## Definition of Done (DoD)

* No function/class is missing a docstring section (Args/Returns/Raises as applicable).  
* All public APIs have type hints and unit/physical dimensions documented where relevant.  
* No `print` statements; uses `logging`.  
* Examples are runnable and concise (\<15 lines per example).  
* No broad `except:` blocks; exceptions are specific and documented.

