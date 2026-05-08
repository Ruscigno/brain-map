#!/usr/bin/env python3
"""One-shot expansion: add a Python root branch with 20 common senior
interview subjects, each with the standard
Definition / Trade-offs / Application Example detail child.

Inserted right after the Golang root so language nodes cluster together.
Idempotent — if a top-level Python node already exists, the script
exits without modifying the file.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "public" / "mindmap.json"


def detail_title(definition: str, trade_offs: str, application: str) -> str:
    return (
        f"**Definition:** {definition}<br/>"
        f"**Trade-offs:** {trade_offs}<br/>"
        f"**Application Example:** {application}"
    )


# ─── 20 leaf titles, in display order ────────────────────────────────────
LEAVES: list[str] = [
    # Core language (8)
    "Data model (everything is an object)",
    "Mutable vs immutable types",
    "Comprehensions (list / dict / set / generator)",
    "Iterators & generators (yield, lazy evaluation)",
    "Decorators (function / class, @property, @staticmethod / @classmethod)",
    "Context managers (`with`, `__enter__` / `__exit__`, contextlib)",
    "Closures & scoping (LEGB, late binding, nonlocal)",
    "Common gotchas (mutable defaults, late-binding closures, copy vs deepcopy)",
    # OO & typing (4)
    "Classes, inheritance & MRO (C3 linearization, super())",
    "Dunder methods (__init__, __repr__, __eq__, __hash__, __iter__, __call__)",
    "Type hints (typing, generics, Protocols, mypy / pyright)",
    "Dataclasses, attrs, Pydantic",
    # Concurrency (4)
    "The GIL",
    "asyncio & coroutines (event loop, async / await)",
    "threading vs multiprocessing",
    "concurrent.futures (ThreadPoolExecutor, ProcessPoolExecutor)",
    # Runtime & ecosystem (4)
    "Memory management (refcount + cyclic GC)",
    "CPython performance (bytecode, C extensions, why Python is 'slow')",
    "Packaging (pip / Poetry / uv, pyproject.toml, virtualenv)",
    "Testing (pytest, fixtures, parametrize, mocking, hypothesis)",
]


# ─── Detail content keyed by leaf title ──────────────────────────────────
DETAILS: dict[str, tuple[str, str, str]] = {
    "Data model (everything is an object)": (
        "Python's data model treats **everything as an object** with attributes and methods (ints, classes, modules, functions). Behaviour is implemented via **dunder methods** (`__init__`, `__add__`, `__iter__`) the language calls in response to operators and built-ins.",
        "Uniform semantics make the language deeply customisable — any class can be made hashable, comparable, iterable, callable — but the indirection costs CPU and the dunder vocabulary is large.",
        "Implementing `__len__` and `__iter__` on a custom collection so `len(c)`, `for x in c`, and `bool(c)` all work without writing extra code.",
    ),
    "Mutable vs immutable types": (
        "**Immutable** types (`int`, `float`, `str`, `tuple`, `frozenset`, `bytes`) cannot change after creation; **mutable** types (`list`, `dict`, `set`, most user classes) can. Immutable values are hashable and safe to share across threads/scopes.",
        "Immutability buys safety and hashability (usable as dict keys / set members) at the cost of allocating a new value on every \"change\"; mutability is efficient but creates aliasing bugs and disqualifies values from being keys.",
        "Using `tuple` of `(user_id, role)` as a dict key for caching permissions; using a `list` for the cache-misses queue because order matters and mutation is frequent.",
    ),
    "Comprehensions (list / dict / set / generator)": (
        "Concise expressions building a new list/dict/set/generator from an iterable: `[x*x for x in xs if x > 0]`, `{k: v for k, v in pairs}`. **Generator expressions** `(x*x for x in xs)` are lazy — no list is built.",
        "More readable than `for`+`append` and faster (one CPython opcode), but nested comprehensions become unreadable past two levels — extract a helper function instead.",
        "`users_by_id = {u.id: u for u in users}` to build a lookup index in one line; `total = sum(x for x in stream if predicate(x))` to aggregate without materialising a list.",
    ),
    "Iterators & generators (yield, lazy evaluation)": (
        "An **iterator** is anything with `__next__` / `__iter__`; a **generator** is a function using `yield` that returns an iterator and pauses/resumes between yields. `yield from` delegates to another iterable.",
        "Constant memory regardless of stream size and natural composition (chain generators), but only single-pass — once consumed, you must re-create. Errors mid-stream are harder to debug because the stack frame is the generator's, not the consumer's.",
        "`def read_logs(p): \\n    with open(p) as f: yield from f` streaming a 50 GB log file line-by-line; chained with `(line for line in read_logs(p) if 'ERROR' in line)` for filtering.",
    ),
    "Decorators (function / class, @property, @staticmethod / @classmethod)": (
        "A callable that takes a function/class and returns a (usually wrapped) function/class. Applied with `@decorator` syntax sugar above the `def`/`class`.",
        "Concise way to add cross-cutting behaviour (logging, caching, auth) without modifying the wrapped code, but obscures what the function actually is — `functools.wraps` is mandatory to preserve `__name__`, `__doc__`, and signatures.",
        "`@functools.lru_cache(maxsize=1024)` to memoise an expensive pure function; `@app.route(\"/users\")` (Flask) registering a handler; `@dataclass` synthesising `__init__`, `__repr__`, `__eq__`.",
    ),
    "Context managers (`with`, `__enter__` / `__exit__`, contextlib)": (
        "Objects with `__enter__` and `__exit__` methods (or wrapped via `@contextmanager`) that bracket a block — used with the `with` statement to guarantee setup/teardown even on exceptions.",
        "Cleaner than try/finally and composable (`with a, b:`), but stacking many context managers across a function quickly gets unreadable — `contextlib.ExitStack` helps for dynamic counts.",
        "`with open(path) as f, db.transaction(), tracer.span(\"import\"):` running an import inside a transaction with a trace span — all three teardowns guaranteed even if the import raises.",
    ),
    "Closures & scoping (LEGB, late binding, nonlocal)": (
        "Python resolves names by **LEGB** (Local → Enclosing → Global → Built-in). A **closure** is an inner function capturing names from an enclosing function's scope. `nonlocal` rebinds an enclosing variable; `global` rebinds a module-level one.",
        "Closures make decorators and small callbacks idiomatic, but capture by **reference** not by value — the classic gotcha is `[lambda: i for i in range(3)]` producing three lambdas that all return `2`.",
        "`def make_adder(n): return lambda x: x + n` — `make_adder(5)(3) == 8`. The fix for the loop gotcha: `lambda i=i: ...` to capture the value at definition time via a default argument.",
    ),
    "Common gotchas (mutable defaults, late-binding closures, copy vs deepcopy)": (
        "Three classics: (1) **mutable default arguments** (`def f(xs=[])` reuses the same list across calls), (2) **late-binding closures** (loops capturing the loop variable, not its value), (3) **copy vs deepcopy** (`list(d)` only copies the outer container).",
        "These behaviours are consistent with Python's evaluation rules but trip everyone at least once — linters (ruff, pylint) catch the first two automatically and `copy.deepcopy` is a one-import fix for the third.",
        "`def append(item, items=None): items = items or []; items.append(item); return items` instead of `items=[]`; `import copy; new = copy.deepcopy(old)` when the structure is nested mutable.",
    ),
    "Classes, inheritance & MRO (C3 linearization, super())": (
        "Multiple inheritance is supported; method resolution follows **C3 linearization** (`Class.__mro__`). `super()` walks the MRO, not just the immediate parent — call order is determined by the declaration order across all bases.",
        "Powerful for mixins (e.g. Django views), but the diamond problem and surprising `super()` ordering make deep multiple-inheritance brittle — composition via dataclasses + Protocols is often cleaner.",
        "Django generic views: `class MyView(LoginRequiredMixin, ListView)` — MRO ensures `dispatch()` calls `LoginRequiredMixin.dispatch()` first, then `ListView`'s, then the base `View`'s.",
    ),
    "Dunder methods (__init__, __repr__, __eq__, __hash__, __iter__, __call__)": (
        "Double-underscore methods Python calls in response to syntax: `__init__` for construction, `__repr__` for debug output, `__eq__` and `__hash__` for equality/hashing, `__iter__`/`__next__` for iteration, `__enter__`/`__exit__` for context, `__call__` to make an instance callable.",
        "Lets user types feel native (any class can be hashable, callable, indexable), but easy to break invariants — defining `__eq__` without `__hash__` makes the class unhashable; defining `__hash__` without matching `__eq__` is a silent bug.",
        "A `Money` value class with `__eq__`, `__hash__`, `__add__`, `__repr__`, `__lt__` so `Money(10, \"USD\") + Money(5, \"USD\")` works and instances can live in sets and dict keys.",
    ),
    "Type hints (typing, generics, Protocols, mypy / pyright)": (
        "Optional static type annotations (PEP 484+) via the `typing` module. **Not enforced at runtime** — `mypy` / `pyright` check them. Generics (`list[int]`, `Callable[[int], str]`), Protocols (structural typing), `TypedDict`, `Self`, `Annotated`.",
        "Massive boost to refactoring safety and editor help, especially in large codebases; the ecosystem still has gaps (missing stubs in old libraries) and type-correctness is a discipline, not a guarantee.",
        "A FastAPI endpoint signature `def create_user(payload: CreateUser, db: Session = Depends(get_db)) -> UserResponse:` — types drive request parsing, validation, response serialisation, AND IDE autocomplete.",
    ),
    "Dataclasses, attrs, Pydantic": (
        "Three libraries that synthesise `__init__`, `__repr__`, `__eq__`, etc. from class attributes. `dataclasses` (stdlib, minimal), `attrs` (older, more features, validators), **Pydantic** (heavier, runtime validation + JSON serialization, FastAPI's default).",
        "All three save boilerplate but pick by need — `dataclass` for simple value objects with no validation, `attrs` for advanced behaviour without runtime cost, **Pydantic** when data crosses an I/O boundary (HTTP, JSON, env).",
        "`@dataclass(frozen=True)` `class Point: x: float; y: float` for an internal value; `class CreateUser(BaseModel): email: EmailStr; age: int = Field(ge=0)` for a request body that needs validation at parse time.",
    ),
    "The GIL": (
        "The **Global Interpreter Lock** — CPython's mutex that allows only one thread to execute Python bytecode at a time. Released around blocking I/O and many C-extension calls.",
        "Makes single-threaded Python fast and CPython internals simple, but caps **CPU-bound** Python code to one core regardless of thread count. PEP 703 (free-threaded CPython) is removing the GIL gradually starting in 3.13.",
        "A web server using threads is fine because each request waits on I/O (DB, network); a CPU-bound numerical pipeline benefits from `multiprocessing`, NumPy (drops the GIL inside C), or PEP 703 free-threaded mode.",
    ),
    "asyncio & coroutines (event loop, async / await)": (
        "Coroutines (`async def` functions) cooperatively yield control via `await`; an **event loop** schedules them. `asyncio.gather(*aws)` runs many concurrently in one thread.",
        "Massive throughput for I/O-heavy workloads (10k+ concurrent connections) on one core, but **colour-aware** — once a function is `async`, callers must be too; mixing sync libraries blocks the loop. CPU-bound work poisons the loop.",
        "An HTTPX scraper fetching 1000 URLs in parallel: `await asyncio.gather(*[client.get(u) for u in urls])` — sequential would be ~10 minutes; concurrent is ~10 seconds limited by network.",
    ),
    "threading vs multiprocessing": (
        "**Threading** runs concurrent tasks in one process under the GIL — good for **I/O-bound**. **Multiprocessing** spawns separate Python processes, each with its own GIL — good for **CPU-bound**; communicates via pickle.",
        "Threads are cheap but GIL-limited; processes give true parallelism at the cost of pickle overhead, slower startup, and shared state being painful (need `Manager`, `Queue`, or `multiprocessing.shared_memory`).",
        "`ThreadPoolExecutor(max_workers=32)` for hammering a remote API; `ProcessPoolExecutor(max_workers=os.cpu_count())` for parallel CPU-bound data transforms over a list of files.",
    ),
    "concurrent.futures (ThreadPoolExecutor, ProcessPoolExecutor)": (
        "High-level API over thread/process pools — `Executor.submit(fn)` returns a `Future`; `as_completed(futures)` iterates as results land; `executor.map(fn, iter)` is a parallel `map`.",
        "Drastically simpler than raw `threading`/`multiprocessing` for fan-out/fan-in, but offers limited control vs `asyncio` for I/O-bound work and is unsuitable for streaming/coroutine-style code.",
        "Parallel-downloading 100 files: `with ThreadPoolExecutor(20) as ex: list(ex.map(download, urls))` — 20 concurrent downloads, results in input order, exceptions raised on the consuming side.",
    ),
    "Memory management (refcount + cyclic GC)": (
        "CPython uses **reference counting** as the primary GC — objects deallocated as soon as their refcount hits zero. A separate **cyclic GC** runs periodically to break reference cycles (linked-list nodes, parent/child trees).",
        "Refcount gives deterministic cleanup (no surprise GC pauses for normal code) but adds per-op CPU cost on every assignment; cyclic GC handles cycles but its `gc.collect()` pause grows with the live-object count.",
        "Profiling memory with `tracemalloc` to find a leak; calling `gc.disable()` in a hot loop where you know there are no cycles, to skip generation-tracing overhead.",
    ),
    "CPython performance (bytecode, C extensions, why Python is 'slow')": (
        "CPython compiles to **bytecode** (`.pyc`) executed by a stack-based interpreter. Speed comes from C extensions (NumPy, Pandas), the C API, and (since 3.11/3.12/3.13) faster interpreter and specialising adaptive optimisations.",
        "Productivity > raw speed for most apps, but pure-Python CPU-bound code is 10–100× slower than equivalent C/Go. Escape hatches: NumPy (vectorised C), Cython, mypyc, PyPy (alternative JIT), or rewriting hot paths in C/Rust via `cffi` / `PyO3`.",
        "A risk-calculation pipeline rewritten as `numpy` array ops drops from 8 minutes (pure-Python loops) to 4 seconds; a hot inner function moved to a Cython module gives a 30× speedup.",
    ),
    "Packaging (pip / Poetry / uv, pyproject.toml, virtualenv)": (
        "Tooling for installing dependencies and shipping projects: `pip` (installer), virtual environments (`venv`, `virtualenv`), `pyproject.toml` (PEP 621 metadata), and managers like **Poetry** / **uv** / **pdm** (resolution + locking).",
        "The ecosystem finally consolidated around `pyproject.toml`, but multiple competing tools (pip+venv vs Poetry vs uv) confuse newcomers. **uv** is currently the fastest and is rapidly winning adoption.",
        "`uv venv && uv pip install -r requirements.txt` for an existing pip project; `uv init && uv add fastapi uvicorn` for a new project — sub-second installs vs Poetry's tens of seconds.",
    ),
    "Testing (pytest, fixtures, parametrize, mocking, hypothesis)": (
        "**pytest** is the de-facto standard — function-style tests, fixtures (`@pytest.fixture`), parametrization (`@pytest.mark.parametrize`), huge plugin ecosystem. **unittest** is stdlib but verbose. **hypothesis** for property-based testing.",
        "pytest's fixtures are powerful but easy to over-engineer (deep fixture trees become hard to debug); parametrization scales test counts without scaling code; mocking via `unittest.mock` is pervasive but mock-heavy tests lock you to the implementation.",
        "`@pytest.mark.parametrize(\"input,expected\", [(1, 1), (2, 4), (3, 9)])` for table-driven tests; `mocker.patch(\"app.repo.get_user\", return_value=...)` (pytest-mock) replacing a DB call in a unit test.",
    ),
}


def build_python_root() -> dict:
    children: list[dict] = []
    missing: list[str] = []
    for title in LEAVES:
        if title not in DETAILS:
            missing.append(title)
            continue
        d, t, x = DETAILS[title]
        children.append(
            {
                "title": title,
                "children": [{"title": detail_title(d, t, x)}],
            }
        )
    if missing:
        raise SystemExit(f"Missing DETAILS entries for: {missing}")
    return {
        "title": "Python",
        "note": "Senior-level Python interview ground — the data model, the GIL, async, typing, packaging, and the gotchas that catch even experienced developers.",
        "children": children,
    }


def main() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    titles = [c["title"] for c in data["children"]]

    if "Python" in titles:
        print("Python root already exists; nothing to do.")
        return

    new_root = build_python_root()

    # Insert right after Golang so language nodes cluster together.
    if "Golang" in titles:
        idx = titles.index("Golang") + 1
    else:
        idx = len(data["children"])
    data["children"].insert(idx, new_root)

    JSON_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Inserted Python root at index {idx} with {len(new_root['children'])} leaves.")


if __name__ == "__main__":
    main()
