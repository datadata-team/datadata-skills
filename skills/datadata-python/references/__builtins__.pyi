# Type stub for the globals injected into RustPython-executed data scripts by
# `python-executor`. Scripts run WITHOUT imports — every name below (the `pl`
# module, `DataFrame`/`Series`, and the host builtins `query`/`fetch`/`args`)
# is injected directly into script scope, so `__builtins__.pyi` is the correct
# mechanism for editor autocompletion/hover.
#
# Hand-written to mirror the Rust implementation. Source of truth:
#   - src/dataframe/mod.rs      (Polars-style DataFrame/Series/Expr pyclasses)
#   - src/fetch_prelude.py      (fetch()/Response/Headers)
#   - src/runtime.rs            (args/print/query/fetch/DataFrame/Series/pl injection)
#
# This file is NOT generated — it must be manually kept in sync whenever the
# Rust API (pymethods/pygetset/pyattr in src/dataframe/mod.rs) changes.

from __future__ import annotations

from typing import Any, Literal, Sequence, overload

# ---------------------------------------------------------------------------
# DataType
# ---------------------------------------------------------------------------

class DataType:
    """A Polars-style logical data type (e.g. ``pl.Int64``, ``pl.String``)."""

    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

# Module-level dtype constants. Precision is not distinguished on the user
# side: Int/Int32/Int64 are all the same physical Int64 type (repr "Int"),
# and Float/Float32/Float64 are all the same physical Float64 type
# (repr "Float") — `pl.Int32 == pl.Int64` and `pl.Float32 == pl.Float64` hold.
Int: DataType
Int32: DataType
Int64: DataType
Float: DataType
Float32: DataType
Float64: DataType
Boolean: DataType
String: DataType
Datetime: DataType
Date: DataType

# ---------------------------------------------------------------------------
# Series
# ---------------------------------------------------------------------------

class Series:
    """An eagerly-evaluated, single typed column of values."""

    @overload
    def __init__(
        self,
        name: str,
        values: Sequence[Any] | None = ...,
        dtype: DataType | None = ...,
        *,
        strict: bool = ...,
        nan_to_null: bool = ...,
    ) -> None: ...
    @overload
    def __init__(
        self,
        values: Sequence[Any] | None = ...,
        name: str | None = ...,
        dtype: DataType | None = ...,
        *,
        strict: bool = ...,
        nan_to_null: bool = ...,
    ) -> None: ...
    @property
    def name(self) -> str:
        """The column name (defaults to ``"series"`` when not given)."""
        ...
    @property
    def dtype(self) -> DataType:
        """The Series' logical data type."""
        ...
    def to_list(self) -> list[Any]:
        """Convert to a plain Python list (nulls become ``None``)."""
        ...
    def abs(self) -> Series:
        """Element-wise absolute value."""
        ...
    def round(self, ndigits: int = ...) -> Series:
        """Round each value to ``ndigits`` decimal places (default 0)."""
        ...
    def fill_null(self, value: Any) -> Series:
        """Replace null values with ``value`` (a scalar; ``None`` is a no-op)."""
        ...
    def is_null(self) -> Series:
        """Boolean Series marking which values are null."""
        ...
    def is_not_null(self) -> Series:
        """Boolean Series marking which values are non-null."""
        ...
    def cast(self, dtype: DataType) -> Series:
        """Cast the Series to another dtype (strict — raises on failure)."""
        ...
    def filter(self, mask: Series) -> Series:
        """Keep only the elements where the boolean ``mask`` is true."""
        ...
    def alias(self, name: str) -> Series:
        """Return a copy of this Series renamed to ``name``."""
        ...
    def rename(self, name: str) -> Series:
        """Return a copy of this Series renamed to ``name`` (alias of ``alias``)."""
        ...
    def sum(self) -> Any:
        """Sum of all non-null values."""
        ...
    def mean(self) -> Any:
        """Arithmetic mean of all non-null values."""
        ...
    def min(self) -> Any:
        """Minimum non-null value."""
        ...
    def max(self) -> Any:
        """Maximum non-null value."""
        ...
    def median(self) -> Any:
        """Median of all non-null values."""
        ...
    def std(self) -> Any:
        """Sample standard deviation of all non-null values."""
        ...
    def var(self) -> Any:
        """Sample variance of all non-null values."""
        ...
    def count(self) -> Any:
        """Count of non-null values."""
        ...
    def n_unique(self) -> Any:
        """Count of distinct values (including null as one distinct value)."""
        ...
    def first(self) -> Any:
        """The first value in the Series."""
        ...
    def last(self) -> Any:
        """The last value in the Series."""
        ...
    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> Any:
        """Get the value at ``index`` (supports negative indices)."""
        ...
    def __repr__(self) -> str: ...
    def __add__(self, other: Series | Any) -> Series: ...
    def __radd__(self, other: Series | Any) -> Series: ...
    def __sub__(self, other: Series | Any) -> Series: ...
    def __rsub__(self, other: Series | Any) -> Series: ...
    def __mul__(self, other: Series | Any) -> Series: ...
    def __rmul__(self, other: Series | Any) -> Series: ...
    def __truediv__(self, other: Series | Any) -> Series: ...
    def __rtruediv__(self, other: Series | Any) -> Series: ...
    def __floordiv__(self, other: Series | Any) -> Series: ...
    def __rfloordiv__(self, other: Series | Any) -> Series: ...
    def __mod__(self, other: Series | Any) -> Series: ...
    def __rmod__(self, other: Series | Any) -> Series: ...
    def __pow__(self, other: Series | Any) -> Series: ...
    def __rpow__(self, other: Series | Any) -> Series: ...
    def __and__(self, other: Series | Any) -> Series: ...
    def __rand__(self, other: Series | Any) -> Series: ...
    def __or__(self, other: Series | Any) -> Series: ...
    def __ror__(self, other: Series | Any) -> Series: ...
    def __invert__(self) -> Series: ...
    def __eq__(self, other: object) -> Series: ...  # type: ignore[override]
    def __ne__(self, other: object) -> Series: ...  # type: ignore[override]
    def __lt__(self, other: Series | Any) -> Series: ...
    def __le__(self, other: Series | Any) -> Series: ...
    def __gt__(self, other: Series | Any) -> Series: ...
    def __ge__(self, other: Series | Any) -> Series: ...

# ---------------------------------------------------------------------------
# Expr (lazy expression tree, evaluated by DataFrame.select/with_columns/filter/group_by.agg)
# ---------------------------------------------------------------------------

class Expr:
    """A lazy, composable column expression built from ``pl.col``/``pl.lit``."""

    def render(self) -> str:
        """Render the expression tree to its debug string form."""
        ...
    def alias(self, name: str) -> Expr:
        """Rename the output column produced by this expression."""
        ...
    def cast(self, dtype: DataType) -> Expr:
        """Cast the expression's result to another dtype."""
        ...
    def is_null(self) -> Expr:
        """Whether each value is null."""
        ...
    def is_not_null(self) -> Expr:
        """Whether each value is non-null."""
        ...
    def fill_null(self, value: Expr | Any) -> Expr:
        """Replace nulls with ``value`` (an expression or scalar)."""
        ...
    def is_in(self, values: Sequence[Any]) -> Expr:
        """Whether each value is a member of ``values``."""
        ...
    def abs(self) -> Expr:
        """Element-wise absolute value."""
        ...
    def round(self, ndigits: int = ...) -> Expr:
        """Round each value to ``ndigits`` decimal places (default 0)."""
        ...
    def sum(self) -> Expr:
        """Aggregation: sum of non-null values."""
        ...
    def mean(self) -> Expr:
        """Aggregation: arithmetic mean of non-null values."""
        ...
    def min(self) -> Expr:
        """Aggregation: minimum non-null value."""
        ...
    def max(self) -> Expr:
        """Aggregation: maximum non-null value."""
        ...
    def median(self) -> Expr:
        """Aggregation: median of non-null values."""
        ...
    def std(self) -> Expr:
        """Aggregation: sample standard deviation of non-null values."""
        ...
    def var(self) -> Expr:
        """Aggregation: sample variance of non-null values."""
        ...
    def count(self) -> Expr:
        """Aggregation: count of non-null values."""
        ...
    def n_unique(self) -> Expr:
        """Aggregation: count of distinct values."""
        ...
    def first(self) -> Expr:
        """Aggregation: the first value."""
        ...
    def last(self) -> Expr:
        """Aggregation: the last value."""
        ...
    @property
    def str(self) -> ExprStr:
        """Namespace for string operations on this expression."""
        ...
    @property
    def dt(self) -> ExprDt:
        """Namespace for datetime/date operations on this expression."""
        ...
    def __add__(self, other: Expr | Any) -> Expr: ...
    def __radd__(self, other: Expr | Any) -> Expr: ...
    def __sub__(self, other: Expr | Any) -> Expr: ...
    def __rsub__(self, other: Expr | Any) -> Expr: ...
    def __mul__(self, other: Expr | Any) -> Expr: ...
    def __rmul__(self, other: Expr | Any) -> Expr: ...
    def __truediv__(self, other: Expr | Any) -> Expr: ...
    def __rtruediv__(self, other: Expr | Any) -> Expr: ...
    def __floordiv__(self, other: Expr | Any) -> Expr: ...
    def __rfloordiv__(self, other: Expr | Any) -> Expr: ...
    def __mod__(self, other: Expr | Any) -> Expr: ...
    def __rmod__(self, other: Expr | Any) -> Expr: ...
    def __pow__(self, other: Expr | Any) -> Expr: ...
    def __rpow__(self, other: Expr | Any) -> Expr: ...
    def __and__(self, other: Expr | Any) -> Expr: ...
    def __rand__(self, other: Expr | Any) -> Expr: ...
    def __or__(self, other: Expr | Any) -> Expr: ...
    def __ror__(self, other: Expr | Any) -> Expr: ...
    def __neg__(self) -> Expr: ...
    def __invert__(self) -> Expr: ...
    # NOTE: unlike normal Python semantics, comparisons on Expr build a lazy
    # boolean expression node and return `Expr`, NOT `bool`.
    def __eq__(self, other: object) -> Expr: ...  # type: ignore[override]
    def __ne__(self, other: object) -> Expr: ...  # type: ignore[override]
    def __lt__(self, other: Expr | Any) -> Expr: ...
    def __le__(self, other: Expr | Any) -> Expr: ...
    def __gt__(self, other: Expr | Any) -> Expr: ...
    def __ge__(self, other: Expr | Any) -> Expr: ...
    def __repr__(self) -> str: ...

class ExprStr:
    """String namespace, reachable only via ``Expr.str`` (not available on Series)."""

    def contains(self, pat: str) -> Expr:
        """Whether the string contains substring ``pat``."""
        ...
    def starts_with(self, pat: str) -> Expr:
        """Whether the string starts with ``pat``."""
        ...
    def ends_with(self, pat: str) -> Expr:
        """Whether the string ends with ``pat``."""
        ...
    def to_uppercase(self) -> Expr:
        """Uppercase the string."""
        ...
    def to_lowercase(self) -> Expr:
        """Lowercase the string."""
        ...
    def strip_chars(self, chars: str | None = ...) -> Expr:
        """Strip leading/trailing whitespace, or the given ``chars`` if provided."""
        ...
    def replace(self, old: str, new: str) -> Expr:
        """Replace the first occurrence of ``old`` with ``new``."""
        ...
    def replace_all(self, old: str, new: str) -> Expr:
        """Replace all occurrences of ``old`` with ``new``."""
        ...
    def len_chars(self) -> Expr:
        """Number of characters in the string."""
        ...
    def slice(self, offset: int, length: int | None = ...) -> Expr:
        """Slice the string starting at ``offset`` for ``length`` characters."""
        ...
    def to_datetime(self, format: str | None = ...) -> Expr:
        """Parse the string to a Datetime, optionally using an explicit ``format``."""
        ...
    def to_date(self, format: str | None = ...) -> Expr:
        """Parse the string to a Date, optionally using an explicit ``format``."""
        ...

class ExprDt:
    """Datetime/date namespace, reachable only via ``Expr.dt`` (not available on Series)."""

    def year(self) -> Expr:
        """Extract the year field."""
        ...
    def month(self) -> Expr:
        """Extract the month field."""
        ...
    def day(self) -> Expr:
        """Extract the day-of-month field."""
        ...
    def hour(self) -> Expr:
        """Extract the hour field."""
        ...
    def minute(self) -> Expr:
        """Extract the minute field."""
        ...
    def second(self) -> Expr:
        """Extract the second field."""
        ...
    def weekday(self) -> Expr:
        """Extract the ISO weekday number."""
        ...
    def truncate(self, every: str) -> Expr:
        """Truncate to a time bucket boundary (e.g. ``"1mo"``, ``"1d"``)."""
        ...
    def strftime(self, format: str) -> Expr:
        """Format as a string using a ``strftime``-style ``format``."""
        ...

# ---------------------------------------------------------------------------
# DataFrame / GroupBy
# ---------------------------------------------------------------------------

class DataFrame:
    """A 2D, column-oriented table of Series sharing the same length."""

    def __init__(
        self,
        data: dict[str, Sequence[Any]]
        | list[dict[str, Any]]
        | list[Series]
        | list[list[Any]]
        | list[tuple[Any, ...]]
        | None = ...,
        schema: dict[str, DataType | None] | list[str] | list[tuple[str, DataType | None]] | None = ...,
        *,
        orient: Literal["row", "col"] | None = ...,
    ) -> None: ...
    @property
    def columns(self) -> list[str]:
        """The column names, in order."""
        ...
    @property
    def dtypes(self) -> list[DataType]:
        """The dtype of each column, in column order."""
        ...
    @property
    def schema(self) -> dict[str, DataType]:
        """Mapping of column name to dtype."""
        ...
    @property
    def shape(self) -> tuple[int, int]:
        """``(height, width)`` — row count and column count."""
        ...
    @property
    def height(self) -> int:
        """Number of rows."""
        ...
    @property
    def width(self) -> int:
        """Number of columns."""
        ...
    def is_empty(self) -> bool:
        """Whether the DataFrame has zero rows."""
        ...
    def select(self, *exprs: Expr | str) -> DataFrame:
        """Evaluate expressions (or bare column names) into a new DataFrame."""
        ...
    def with_columns(self, *exprs: Expr | str) -> DataFrame:
        """Add or overwrite columns, keeping all existing columns."""
        ...
    def filter(self, predicate: Expr | str) -> DataFrame:
        """Keep only the rows where ``predicate`` evaluates to true."""
        ...
    def group_by(self, *keys: str) -> GroupBy:
        """Group rows by one or more column names."""
        ...
    def to_dicts(self) -> list[dict[str, Any]]:
        """Convert to a list of row dicts."""
        ...
    def rows(self) -> list[tuple[Any, ...]]:
        """Convert to a list of row tuples."""
        ...
    def to_dict(self) -> dict[str, list[Any]]:
        """Convert to a dict of column name -> list of values."""
        ...
    def get_column(self, name: str) -> Series:
        """Get a single column as a Series by name."""
        ...
    def __getitem__(self, key: str) -> Series:
        """Get a single column as a Series by name (raises ``KeyError`` if missing)."""
        ...
    def __len__(self) -> int:
        """Number of rows (same as ``height``)."""
        ...
    def __repr__(self) -> str: ...

class GroupBy:
    """A grouped view of a DataFrame, produced by ``DataFrame.group_by``."""

    def agg(self, *exprs: Expr | str) -> DataFrame:
        """Aggregate each group; every expression must reduce to a single value."""
        ...

# ---------------------------------------------------------------------------
# fetch() — from src/fetch_prelude.py
# ---------------------------------------------------------------------------

class Headers:
    """Case-insensitive response headers, as returned by ``Response.headers``."""

    def get(self, name: str, default: Any | None = ...) -> Any:
        """Get a header value by name (case-insensitive), or ``default``."""
        ...

class Response:
    """The result of a ``fetch()`` call."""

    ok: bool
    status: int
    status_text: str
    headers: Headers
    def text(self) -> str:
        """The raw response body as a string."""
        ...
    def json(self) -> Any:
        """Parse the response body as JSON."""
        ...

def fetch(
    url: str,
    method: str = ...,
    body: Any = ...,
    headers: dict[str, str] | None = ...,
    timeout: float = ...,
) -> Response:
    """Perform an HTTP request. ``body`` is JSON-encoded automatically unless it is already a str.

    Raises an exception on transport-level errors; HTTP error status codes do
    not raise — check ``response.ok`` / ``response.status`` instead.
    """
    ...

# ---------------------------------------------------------------------------
# pl namespace
# ---------------------------------------------------------------------------

class _Pl:
    """The ``pl`` namespace: expression constructors, dtypes, and the DataFrame/Series types."""

    DataFrame: type[DataFrame]
    Series: type[Series]
    Int: DataType
    Int32: DataType
    Int64: DataType
    Float: DataType
    Float32: DataType
    Float64: DataType
    Boolean: DataType
    String: DataType
    Datetime: DataType
    Date: DataType
    def col(self, name: str) -> Expr:
        """Reference a column by name."""
        ...
    def lit(self, value: int | float | str | bool | None) -> Expr:
        """Build a literal expression from a scalar value."""
        ...

pl: _Pl

# ---------------------------------------------------------------------------
# Host builtins
# ---------------------------------------------------------------------------

def query(sql: str, *args: Any) -> DataFrame:
    """Run a SQL query against the attached data source(s) and return the result rows as a DataFrame.

    Note: SQL timestamp/date columns come back as String columns — use `.str.to_datetime()`
    (or `.str.to_date()`) to convert them.
    """
    ...

args: dict[str, Any]
"""Script input parameters, passed in by the caller (always a dict)."""
