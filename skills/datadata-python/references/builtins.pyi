# Type stub for the globals injected into RustPython-executed data scripts by
# `python-executor`. Scripts run WITHOUT imports — every name below (the `pl`
# module, `DataFrame`/`Series`, and the host builtins `query`/`fetch`/`args`)
# is injected directly into script scope, so `builtins.pyi` is the correct
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

from typing import Any, Callable, Literal, Sequence, overload

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
    def skew(self, bias: bool = ...) -> Any:
        """Sample skewness of all non-null values (``bias=True`` default: population moment estimator)."""
        ...
    def kurtosis(self, fisher: bool = ..., bias: bool = ...) -> Any:
        """Kurtosis of all non-null values (``fisher=True`` default: excess kurtosis; ``bias=True`` default)."""
        ...
    def mode(self) -> Series:
        """The most frequently occurring value(s) (may return more than one)."""
        ...
    def quantile(self, quantile: float, interpolation: Literal["nearest"] = ...) -> Any:
        """The value at the given quantile (0..1). Only ``interpolation="nearest"`` (the default) is implemented."""
        ...
    def rolling_min(
        self,
        window_size: int,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Series:
        """Rolling minimum over a fixed-size window (``weights`` unsupported — must be ``None``)."""
        ...
    def rolling_max(
        self,
        window_size: int,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Series:
        """Rolling maximum over a fixed-size window (``weights`` unsupported — must be ``None``)."""
        ...
    def rolling_sum(
        self,
        window_size: int,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Series:
        """Rolling sum over a fixed-size window (``weights`` unsupported — must be ``None``)."""
        ...
    def rolling_mean(
        self,
        window_size: int,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Series:
        """Rolling arithmetic mean over a fixed-size window (``weights`` unsupported — must be ``None``)."""
        ...
    def rolling_median(
        self,
        window_size: int,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Series:
        """Rolling median over a fixed-size window (``weights`` unsupported — must be ``None``)."""
        ...
    def rolling_std(
        self,
        window_size: int,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
        ddof: int = ...,
    ) -> Series:
        """Rolling sample standard deviation over a fixed-size window (``ddof`` default 1)."""
        ...
    def rolling_var(
        self,
        window_size: int,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
        ddof: int = ...,
    ) -> Series:
        """Rolling sample variance over a fixed-size window (``ddof`` default 1)."""
        ...
    def rolling_skew(
        self,
        window_size: int,
        *,
        bias: bool = ...,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Series:
        """Rolling skewness over a fixed-size window (no ``weights`` param, mirroring Polars)."""
        ...
    def rolling_kurtosis(
        self,
        window_size: int,
        *,
        fisher: bool = ...,
        bias: bool = ...,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Series:
        """Rolling kurtosis over a fixed-size window (no ``weights`` param, mirroring Polars)."""
        ...
    def rolling_quantile(
        self,
        quantile: float,
        interpolation: Literal["nearest"] = ...,
        window_size: int = ...,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Series:
        """Rolling quantile over a fixed-size window (``window_size`` default 2; only ``"nearest"`` interpolation)."""
        ...
    def rolling_map(
        self,
        function: Callable[[Series], Any],
        window_size: int,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Series:
        """Apply ``function`` to each window (packaged as a ``Series``), taking its scalar return as the output."""
        ...
    def rolling_min_by(
        self,
        by: Series,
        window: str,
        *,
        min_samples: int = ...,
        closed: Literal["left", "right", "both", "none"] = ...,
    ) -> Series:
        """Rolling minimum over a time/key window: ``by`` (another Series, assumed sorted ascending) defines each
        row's window via a duration string (e.g. ``"2d"``); ``closed`` defaults to ``"right"``.
        """
        ...
    def rolling_max_by(
        self,
        by: Series,
        window: str,
        *,
        min_samples: int = ...,
        closed: Literal["left", "right", "both", "none"] = ...,
    ) -> Series:
        """Rolling maximum over a time/key window (see ``rolling_min_by``)."""
        ...
    def rolling_sum_by(
        self,
        by: Series,
        window: str,
        *,
        min_samples: int = ...,
        closed: Literal["left", "right", "both", "none"] = ...,
    ) -> Series:
        """Rolling sum over a time/key window (see ``rolling_min_by``)."""
        ...
    def rolling_mean_by(
        self,
        by: Series,
        window: str,
        *,
        min_samples: int = ...,
        closed: Literal["left", "right", "both", "none"] = ...,
    ) -> Series:
        """Rolling arithmetic mean over a time/key window (see ``rolling_min_by``)."""
        ...
    def rolling_median_by(
        self,
        by: Series,
        window: str,
        *,
        min_samples: int = ...,
        closed: Literal["left", "right", "both", "none"] = ...,
    ) -> Series:
        """Rolling median over a time/key window (see ``rolling_min_by``)."""
        ...
    def rolling_std_by(
        self,
        by: Series,
        window: str,
        *,
        min_samples: int = ...,
        closed: Literal["left", "right", "both", "none"] = ...,
        ddof: int = ...,
    ) -> Series:
        """Rolling sample standard deviation over a time/key window (``ddof`` default 1; see ``rolling_min_by``)."""
        ...
    def rolling_var_by(
        self,
        by: Series,
        window: str,
        *,
        min_samples: int = ...,
        closed: Literal["left", "right", "both", "none"] = ...,
        ddof: int = ...,
    ) -> Series:
        """Rolling sample variance over a time/key window (``ddof`` default 1; see ``rolling_min_by``)."""
        ...
    def ewm_mean(
        self,
        *,
        com: float | None = ...,
        span: float | None = ...,
        half_life: float | None = ...,
        alpha: float | None = ...,
        adjust: bool = ...,
        min_samples: int = ...,
        ignore_nulls: bool = ...,
    ) -> Series:
        """Exponentially-weighted moving average. Provide exactly one of ``com``/``span``/``half_life``/``alpha``."""
        ...
    def ewm_sum(
        self,
        *,
        com: float | None = ...,
        span: float | None = ...,
        half_life: float | None = ...,
        alpha: float | None = ...,
        adjust: bool = ...,
        min_samples: int = ...,
        ignore_nulls: bool = ...,
    ) -> Series:
        """Exponentially-weighted moving sum (see ``ewm_mean`` for the alpha-source params)."""
        ...
    def ewm_var(
        self,
        *,
        com: float | None = ...,
        span: float | None = ...,
        half_life: float | None = ...,
        alpha: float | None = ...,
        adjust: bool = ...,
        min_samples: int = ...,
        ignore_nulls: bool = ...,
        bias: bool = ...,
    ) -> Series:
        """Exponentially-weighted moving variance (``bias=False`` default applies a reliability correction)."""
        ...
    def ewm_std(
        self,
        *,
        com: float | None = ...,
        span: float | None = ...,
        half_life: float | None = ...,
        alpha: float | None = ...,
        adjust: bool = ...,
        min_samples: int = ...,
        ignore_nulls: bool = ...,
        bias: bool = ...,
    ) -> Series:
        """Exponentially-weighted moving standard deviation (see ``ewm_var``)."""
        ...
    def diff(self, n: int = ..., null_behavior: Literal["ignore"] = ...) -> Series:
        """Difference between each element and the one ``n`` positions before it (default ``n=1``).

        Only ``null_behavior="ignore"`` (the default) is implemented; passing ``"drop"`` raises
        (it would change the output length, which is out of scope).
        """
        ...
    def cum_sum(self, *, reverse: bool = ...) -> Series:
        """Cumulative sum (``reverse=True`` accumulates from the end)."""
        ...
    def cum_prod(self, *, reverse: bool = ...) -> Series:
        """Cumulative product (``reverse=True`` accumulates from the end)."""
        ...
    def pct_change(self, n: int = ...) -> Series:
        """Percentage change versus the value ``n`` positions before (default ``n=1``); always returns Float64."""
        ...
    def sort(self, *, descending: bool = ..., nulls_last: bool = ...) -> Series:
        """Sort by value (stable). Nulls sort first by default, or last with ``nulls_last=True``."""
        ...
    def forward_fill(self, limit: int | None = ...) -> Series:
        """Fill nulls with the last non-null value seen (``limit`` caps consecutive fills; ``None`` = unlimited)."""
        ...
    def backward_fill(self, limit: int | None = ...) -> Series:
        """Fill nulls with the next non-null value (``limit`` caps consecutive fills; ``None`` = unlimited)."""
        ...
    def unique(self, *, maintain_order: bool = ...) -> Series:
        """Distinct values (``maintain_order=True`` preserves first-occurrence order instead of sorting)."""
        ...
    def shift(self, n: int = ..., *, fill_value: Any | None = ...) -> Series:
        """Shift values by ``n`` positions (default 1; negative shifts toward the start).

        Vacated positions become null, or ``fill_value`` if given.
        """
        ...
    def interpolate(self, method: Literal["linear"] = ...) -> Series:
        """Fill nulls by linear interpolation between the nearest non-null neighbors.

        Only ``method="linear"`` (the default) is implemented. Leading/trailing
        nulls with no non-null value on one side stay null.
        """
        ...
    def head(self, n: int = ...) -> Series:
        """The first ``n`` rows (default 5; negative ``n`` drops the last ``|n|`` rows instead)."""
        ...
    def tail(self, n: int = ...) -> Series:
        """The last ``n`` rows (default 5; negative ``n`` drops the first ``|n|`` rows instead)."""
        ...
    def slice(self, offset: int, length: int | None = ...) -> Series:
        """Rows from ``offset`` (negative counts from the end) for ``length`` rows (``None`` = to the end)."""
        ...
    def gather_every(self, n: int, offset: int = ...) -> Series:
        """Every ``n``-th row, starting at ``offset`` (default 0). ``n`` must be >= 1."""
        ...
    def sample(
        self,
        n: int | None = ...,
        *,
        fraction: float | None = ...,
        with_replacement: bool = ...,
        shuffle: bool = ...,
        seed: int | None = ...,
    ) -> Series:
        """Randomly sample rows. Give either ``n`` (row count) or ``fraction`` (of height), not both;
        neither given defaults to ``n=1``. Without replacement, sampling more rows than exist raises.

        ``shuffle=False`` (default) returns picked rows in original order; ``shuffle=True`` returns
        them in draw order. ``seed=None`` draws from a per-execution global PRNG seeded once from host
        entropy (so results vary run to run and successive calls don't repeat); a fixed ``seed`` makes
        the draw reproducible **within this engine only** — it is NOT byte-identical to what Polars'
        own sampling would pick for the same seed.
        """
        ...
    def top_k(self, k: int = ...) -> Series:
        """The ``k`` largest values (default ``k=5``)."""
        ...
    def bottom_k(self, k: int = ...) -> Series:
        """The ``k`` smallest values (default ``k=5``)."""
        ...
    def replace_strict(
        self,
        old: Sequence[Any],
        new: Sequence[Any],
        *,
        default: Any | None = ...,
        return_dtype: DataType | None = ...,
    ) -> Series:
        """Replace each value found in ``old`` with the value at the same position in ``new``.

        A value not found in ``old`` becomes ``default`` (``None`` if omitted) rather than passing through
        unchanged — this is the "strict" variant.
        """
        ...
    def value_counts(
        self,
        *,
        sort: bool = ...,
        parallel: bool = ...,
        name: str | None = ...,
        normalize: bool = ...,
    ) -> DataFrame:
        """Count occurrences of each distinct value, returned as a two-column DataFrame.

        The value column keeps this Series' ``name``; the count column is named ``"count"`` (or
        ``"proportion"`` when ``normalize=True``) unless overridden via ``name``. ``parallel`` is accepted but
        not used (no parallel implementation).
        """
        ...
    def map_elements(
        self,
        function: Callable[[Any], Any],
        return_dtype: DataType | None = ...,
        skip_nulls: bool = ...,
    ) -> Series:
        """Apply a Python callback to each element, returning a new Series.

        ``skip_nulls`` (default ``True``) skips calling ``function`` on null
        elements (the output stays null there). ``return_dtype`` is inferred
        from the callback's results when not given.
        """
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
    def skew(self, bias: bool = ...) -> Expr:
        """Aggregation: sample skewness (``bias=True`` default: population moment estimator)."""
        ...
    def kurtosis(self, fisher: bool = ..., bias: bool = ...) -> Expr:
        """Aggregation: kurtosis (``fisher=True`` default: excess kurtosis; ``bias=True`` default)."""
        ...
    def mode(self) -> Expr:
        """Aggregation: the most frequently occurring value(s)."""
        ...
    def quantile(self, quantile: float, interpolation: Literal["nearest"] = ...) -> Expr:
        """Aggregation: the value at the given quantile (0..1). Only ``interpolation="nearest"`` is implemented."""
        ...
    def rolling_min(
        self,
        window_size: int,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Expr:
        """Rolling minimum over a fixed-size window (``weights`` unsupported — must be ``None``)."""
        ...
    def rolling_max(
        self,
        window_size: int,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Expr:
        """Rolling maximum over a fixed-size window (``weights`` unsupported — must be ``None``)."""
        ...
    def rolling_sum(
        self,
        window_size: int,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Expr:
        """Rolling sum over a fixed-size window (``weights`` unsupported — must be ``None``)."""
        ...
    def rolling_mean(
        self,
        window_size: int,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Expr:
        """Rolling arithmetic mean over a fixed-size window (``weights`` unsupported — must be ``None``)."""
        ...
    def rolling_median(
        self,
        window_size: int,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Expr:
        """Rolling median over a fixed-size window (``weights`` unsupported — must be ``None``)."""
        ...
    def rolling_std(
        self,
        window_size: int,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
        ddof: int = ...,
    ) -> Expr:
        """Rolling sample standard deviation over a fixed-size window (``ddof`` default 1)."""
        ...
    def rolling_var(
        self,
        window_size: int,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
        ddof: int = ...,
    ) -> Expr:
        """Rolling sample variance over a fixed-size window (``ddof`` default 1)."""
        ...
    def rolling_skew(
        self,
        window_size: int,
        *,
        bias: bool = ...,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Expr:
        """Rolling skewness over a fixed-size window (no ``weights`` param, mirroring Polars)."""
        ...
    def rolling_kurtosis(
        self,
        window_size: int,
        *,
        fisher: bool = ...,
        bias: bool = ...,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Expr:
        """Rolling kurtosis over a fixed-size window (no ``weights`` param, mirroring Polars)."""
        ...
    def rolling_quantile(
        self,
        quantile: float,
        interpolation: Literal["nearest"] = ...,
        window_size: int = ...,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Expr:
        """Rolling quantile over a fixed-size window (``window_size`` default 2; only ``"nearest"`` interpolation)."""
        ...
    def rolling_map(
        self,
        function: Callable[[Series], Any],
        window_size: int,
        weights: None = ...,
        *,
        min_samples: int | None = ...,
        center: bool = ...,
    ) -> Expr:
        """Apply ``function`` to each window (packaged as a ``Series``), taking its scalar return as the output."""
        ...
    def rolling_min_by(
        self,
        by: str | Expr,
        window: str,
        *,
        min_samples: int = ...,
        closed: Literal["left", "right", "both", "none"] = ...,
    ) -> Expr:
        """Rolling minimum over a time/key window: ``by`` (a column name or another expression, assumed sorted
        ascending when evaluated) defines each row's window via a duration string (e.g. ``"2d"``); ``closed``
        defaults to ``"right"``.
        """
        ...
    def rolling_max_by(
        self,
        by: str | Expr,
        window: str,
        *,
        min_samples: int = ...,
        closed: Literal["left", "right", "both", "none"] = ...,
    ) -> Expr:
        """Rolling maximum over a time/key window (see ``rolling_min_by``)."""
        ...
    def rolling_sum_by(
        self,
        by: str | Expr,
        window: str,
        *,
        min_samples: int = ...,
        closed: Literal["left", "right", "both", "none"] = ...,
    ) -> Expr:
        """Rolling sum over a time/key window (see ``rolling_min_by``)."""
        ...
    def rolling_mean_by(
        self,
        by: str | Expr,
        window: str,
        *,
        min_samples: int = ...,
        closed: Literal["left", "right", "both", "none"] = ...,
    ) -> Expr:
        """Rolling arithmetic mean over a time/key window (see ``rolling_min_by``)."""
        ...
    def rolling_median_by(
        self,
        by: str | Expr,
        window: str,
        *,
        min_samples: int = ...,
        closed: Literal["left", "right", "both", "none"] = ...,
    ) -> Expr:
        """Rolling median over a time/key window (see ``rolling_min_by``)."""
        ...
    def rolling_std_by(
        self,
        by: str | Expr,
        window: str,
        *,
        min_samples: int = ...,
        closed: Literal["left", "right", "both", "none"] = ...,
        ddof: int = ...,
    ) -> Expr:
        """Rolling sample standard deviation over a time/key window (``ddof`` default 1; see ``rolling_min_by``)."""
        ...
    def rolling_var_by(
        self,
        by: str | Expr,
        window: str,
        *,
        min_samples: int = ...,
        closed: Literal["left", "right", "both", "none"] = ...,
        ddof: int = ...,
    ) -> Expr:
        """Rolling sample variance over a time/key window (``ddof`` default 1; see ``rolling_min_by``)."""
        ...
    def ewm_mean(
        self,
        *,
        com: float | None = ...,
        span: float | None = ...,
        half_life: float | None = ...,
        alpha: float | None = ...,
        adjust: bool = ...,
        min_samples: int = ...,
        ignore_nulls: bool = ...,
    ) -> Expr:
        """Exponentially-weighted moving average. Provide exactly one of ``com``/``span``/``half_life``/``alpha``."""
        ...
    def ewm_sum(
        self,
        *,
        com: float | None = ...,
        span: float | None = ...,
        half_life: float | None = ...,
        alpha: float | None = ...,
        adjust: bool = ...,
        min_samples: int = ...,
        ignore_nulls: bool = ...,
    ) -> Expr:
        """Exponentially-weighted moving sum (see ``ewm_mean`` for the alpha-source params)."""
        ...
    def ewm_var(
        self,
        *,
        com: float | None = ...,
        span: float | None = ...,
        half_life: float | None = ...,
        alpha: float | None = ...,
        adjust: bool = ...,
        min_samples: int = ...,
        ignore_nulls: bool = ...,
        bias: bool = ...,
    ) -> Expr:
        """Exponentially-weighted moving variance (``bias=False`` default applies a reliability correction)."""
        ...
    def ewm_std(
        self,
        *,
        com: float | None = ...,
        span: float | None = ...,
        half_life: float | None = ...,
        alpha: float | None = ...,
        adjust: bool = ...,
        min_samples: int = ...,
        ignore_nulls: bool = ...,
        bias: bool = ...,
    ) -> Expr:
        """Exponentially-weighted moving standard deviation (see ``ewm_var``)."""
        ...
    def diff(self, n: int = ..., null_behavior: Literal["ignore"] = ...) -> Expr:
        """Difference between each element and the one ``n`` positions before it (default ``n=1``).

        Only ``null_behavior="ignore"`` (the default) is implemented; passing ``"drop"`` raises
        (it would change the output length, which is out of scope).
        """
        ...
    def cum_sum(self, *, reverse: bool = ...) -> Expr:
        """Cumulative sum (``reverse=True`` accumulates from the end)."""
        ...
    def cum_prod(self, *, reverse: bool = ...) -> Expr:
        """Cumulative product (``reverse=True`` accumulates from the end)."""
        ...
    def pct_change(self, n: int = ...) -> Expr:
        """Percentage change versus the value ``n`` positions before (default ``n=1``); always returns Float64."""
        ...
    def sort(self, *, descending: bool = ..., nulls_last: bool = ...) -> Expr:
        """Sort by value (stable). Nulls sort first by default, or last with ``nulls_last=True``."""
        ...
    def forward_fill(self, limit: int | None = ...) -> Expr:
        """Fill nulls with the last non-null value seen (``limit`` caps consecutive fills; ``None`` = unlimited)."""
        ...
    def backward_fill(self, limit: int | None = ...) -> Expr:
        """Fill nulls with the next non-null value (``limit`` caps consecutive fills; ``None`` = unlimited)."""
        ...
    def unique(self, *, maintain_order: bool = ...) -> Expr:
        """Distinct values (``maintain_order=True`` preserves first-occurrence order instead of sorting)."""
        ...
    def shift(self, n: int = ..., *, fill_value: Any | None = ...) -> Expr:
        """Shift values by ``n`` positions (default 1; negative shifts toward the start).

        Vacated positions become null, or ``fill_value`` if given.
        """
        ...
    def interpolate(self, method: Literal["linear"] = ...) -> Expr:
        """Fill nulls by linear interpolation between the nearest non-null neighbors.

        Only ``method="linear"`` (the default) is implemented. Leading/trailing
        nulls with no non-null value on one side stay null.
        """
        ...
    def top_k(self, k: int = ...) -> Expr:
        """The ``k`` largest values (default ``k=5``)."""
        ...
    def bottom_k(self, k: int = ...) -> Expr:
        """The ``k`` smallest values (default ``k=5``)."""
        ...
    def replace_strict(
        self,
        old: Sequence[Any],
        new: Sequence[Any],
        *,
        default: Any | None = ...,
        return_dtype: DataType | None = ...,
    ) -> Expr:
        """Replace each value found in ``old`` with the value at the same position in ``new``.

        A value not found in ``old`` becomes ``default`` (``None`` if omitted) rather than passing through
        unchanged — this is the "strict" variant.
        """
        ...
    def over(
        self,
        *partition_by: str | Expr,
        mapping_strategy: Literal["group_to_rows"] = ...,
    ) -> Expr:
        """Window function: evaluate this expression per partition (grouped by ``partition_by``), then broadcast
        each group's result back to its original rows. At least one ``partition_by`` column/expression is
        required; only ``mapping_strategy="group_to_rows"`` (the default) is implemented.
        """
        ...
    def map_elements(
        self,
        function: Callable[[Any], Any],
        return_dtype: DataType | None = ...,
        skip_nulls: bool = ...,
    ) -> Expr:
        """Apply a Python callback to each element, lazily, returning a new expression.

        ``skip_nulls`` (default ``True``) skips calling ``function`` on null
        elements (the output stays null there). ``return_dtype`` is inferred
        from the callback's results when not given.
        """
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
# when/then/otherwise (conditional expression builder), built via ``pl.when``
# ---------------------------------------------------------------------------

class When:
    """Builder returned by ``pl.when(...)``; call ``.then()`` to attach a branch value."""

    def then(self, value: Expr | Any) -> Then:
        """Attach the value/expression used when this branch's condition is true."""
        ...

class Then:
    """Builder returned by ``When.then()``.

    Chain ``.when()`` to add further conditional branches, or finish the
    expression with ``.otherwise()``/``.alias()``.
    """

    def when(self, condition: Expr | Any) -> When:
        """Start another conditional branch."""
        ...
    def otherwise(self, value: Expr | Any) -> Expr:
        """Finish the expression, using ``value`` where no branch condition matched."""
        ...
    def alias(self, name: str) -> Expr:
        """Finish the expression (unmatched rows are null) and rename the output column."""
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
    def head(self, n: int = ...) -> DataFrame:
        """The first ``n`` rows (default 5; negative ``n`` drops the last ``|n|`` rows instead)."""
        ...
    def tail(self, n: int = ...) -> DataFrame:
        """The last ``n`` rows (default 5; negative ``n`` drops the first ``|n|`` rows instead)."""
        ...
    def limit(self, n: int = ...) -> DataFrame:
        """Alias for ``head``."""
        ...
    def slice(self, offset: int, length: int | None = ...) -> DataFrame:
        """Rows from ``offset`` (negative counts from the end) for ``length`` rows (``None`` = to the end)."""
        ...
    def gather_every(self, n: int, offset: int = ...) -> DataFrame:
        """Every ``n``-th row, starting at ``offset`` (default 0). ``n`` must be >= 1."""
        ...
    def sample(
        self,
        n: int | None = ...,
        *,
        fraction: float | None = ...,
        with_replacement: bool = ...,
        shuffle: bool = ...,
        seed: int | None = ...,
    ) -> DataFrame:
        """Randomly sample rows. Give either ``n`` (row count) or ``fraction`` (of height), not both;
        neither given defaults to ``n=1``. Without replacement, sampling more rows than exist raises.

        ``shuffle=False`` (default) returns picked rows in original order; ``shuffle=True`` returns
        them in draw order. ``seed=None`` draws from a per-execution global PRNG seeded once from host
        entropy (so results vary run to run and successive calls don't repeat); a fixed ``seed`` makes
        the draw reproducible **within this engine only** — it is NOT byte-identical to what Polars'
        own sampling would pick for the same seed.
        """
        ...
    def unique(
        self,
        subset: str | Sequence[str] | None = ...,
        *,
        keep: Literal["first", "last", "any", "none"] = ...,
        maintain_order: bool = ...,
    ) -> DataFrame:
        """Drop duplicate rows, comparing only ``subset`` columns (default: all columns).

        ``keep`` picks which row of each duplicate group survives: ``"first"``/``"any"`` keep the
        first, ``"last"`` the last, ``"none"`` drops every row that has any duplicate. ``maintain_order``
        is accepted for Polars API compatibility but has no effect — output order is already
        first-occurrence-stable.
        """
        ...
    def n_unique(self, subset: str | Sequence[str] | None = ...) -> int:
        """Count of distinct rows, comparing only ``subset`` columns (default: all columns)."""
        ...
    def sort(
        self,
        by: str | Sequence[str],
        *,
        descending: bool | Sequence[bool] = ...,
        nulls_last: bool | Sequence[bool] = ...,
        maintain_order: bool = ...,
    ) -> DataFrame:
        """Sort rows by one or more columns (stable). ``by`` is a column name or list of column names
        (no expression support). ``descending``/``nulls_last`` each take either a single bool (broadcast
        to every sort key) or a list of bools matching ``by`` in length (per-key control). Sorting is
        already stable, so ``maintain_order`` is accepted but has no additional effect.
        """
        ...
    def sum(self) -> DataFrame:
        """Sum each column independently, collapsed to a single row. Columns that don't support
        summation (e.g. strings) become null rather than raising."""
        ...
    def mean(self) -> DataFrame:
        """Arithmetic mean of each column independently, collapsed to a single row."""
        ...
    def min(self) -> DataFrame:
        """Minimum of each column independently, collapsed to a single row."""
        ...
    def max(self) -> DataFrame:
        """Maximum of each column independently, collapsed to a single row."""
        ...
    def median(self) -> DataFrame:
        """Median of each column independently, collapsed to a single row."""
        ...
    def std(self) -> DataFrame:
        """Sample standard deviation of each column independently, collapsed to a single row."""
        ...
    def var(self) -> DataFrame:
        """Sample variance of each column independently, collapsed to a single row."""
        ...
    def count(self) -> DataFrame:
        """Non-null count of each column independently, collapsed to a single row."""
        ...
    def shift(self, n: int = ..., *, fill_value: Any | None = ...) -> DataFrame:
        """Shift every column's values by ``n`` positions (default 1; negative shifts toward the
        start). Vacated positions become null, or ``fill_value`` if given. Column names/count unchanged.
        """
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
    def group_by_dynamic(
        self,
        index_column: str,
        *,
        every: str,
        period: str | None = ...,
        offset: str | None = ...,
        closed: Literal["left", "right", "both", "none"] = ...,
        label: Literal["left", "right", "datapoint"] = ...,
        group_by: str | Sequence[str] | None = ...,
        start_by: Literal["window"] = ...,
    ) -> DynamicGroupBy:
        """Group rows into dynamic (rolling) time windows over ``index_column``.

        ``index_column`` must be Datetime or Date. ``every`` is the step between
        window starts (duration string, e.g. ``"2d"``); ``period`` is the window
        width and defaults to ``every`` (tumbling windows). ``offset`` shifts the
        window boundaries and defaults to no offset. ``closed`` picks which
        boundary is inclusive (default ``"left"``); ``label`` picks which
        boundary is used for the window's index value in the output (default
        ``"left"``). ``group_by`` additionally partitions rows by key column(s)
        before windowing. Only ``start_by="window"`` is supported.
        """
        ...
    def upsample(
        self,
        time_column: str,
        *,
        every: str,
        group_by: str | Sequence[str] | None = ...,
        maintain_order: bool = ...,
    ) -> DataFrame:
        """Insert missing rows to make ``time_column`` a regular grid stepped by ``every``.

        ``time_column`` must be Datetime or Date. Grid points that don't match
        an existing row are inserted with all other columns null (use
        ``Expr.forward_fill`` / ``backward_fill`` afterwards to fill them).
        ``group_by`` builds one independent grid per key group. Rows whose
        ``time_column`` value falls off the regular grid are dropped from the
        output; when multiple rows share a grid timestamp, the first is kept.
        """
        ...
    def join(
        self,
        other: DataFrame,
        on: str | Sequence[str] | None = ...,
        how: Literal["inner", "left", "right", "full", "cross", "semi", "anti"] = ...,
        *,
        left_on: str | Sequence[str] | None = ...,
        right_on: str | Sequence[str] | None = ...,
        suffix: str = ...,
        nulls_equal: bool = ...,
        coalesce: bool | None = ...,
    ) -> DataFrame:
        """Join with another DataFrame.

        Provide either ``on`` (same key name(s) on both sides) or both
        ``left_on``/``right_on``. ``how`` defaults to ``"inner"``; ``"outer"`` is
        accepted as an alias for ``"full"``. ``how="cross"`` takes no keys and
        produces the Cartesian product. ``suffix`` disambiguates overlapping
        non-key column names. ``nulls_equal`` controls whether null keys match
        each other (default ``False``). ``coalesce`` merges each side's key
        column into one; left unset it defaults to ``True`` for every ``how``
        except ``"full"`` (where both key columns are kept, matching Polars).
        """
        ...
    def join_where(self, other: DataFrame, *predicates: Expr, suffix: str = ...) -> DataFrame:
        """Inner join on arbitrary (non-equi) predicate expressions, AND-ed together.

        Builds the Cartesian product internally, then filters by the
        predicates. A predicate referencing a right-table column whose name
        collides with a left-table column must use the ``suffix``-qualified name.
        """
        ...
    def join_asof(
        self,
        other: DataFrame,
        *,
        on: str | None = ...,
        left_on: str | None = ...,
        right_on: str | None = ...,
        by: str | Sequence[str] | None = ...,
        by_left: str | Sequence[str] | None = ...,
        by_right: str | Sequence[str] | None = ...,
        strategy: Literal["backward", "forward", "nearest"] = ...,
        suffix: str = ...,
        tolerance: int | float | str | None = ...,
        allow_exact_matches: bool = ...,
        coalesce: bool = ...,
    ) -> DataFrame:
        """Nearest-key join against a single key column (Polars-style asof join).

        Provide either ``on`` (same key name on both sides) or both
        ``left_on``/``right_on``; optionally add exact-match grouping key(s)
        via ``by`` or ``by_left``/``by_right``. ``strategy`` picks the match
        direction (default ``"backward"``). ``tolerance`` bounds how far a
        match may be — a number for numeric keys, or a duration string (e.g.
        ``"1d"``) when the key is Datetime/Date. ``coalesce`` defaults to ``True``.
        """
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
    def sum(self) -> DataFrame:
        """Shortcut for ``.agg(pl.col(c).sum() for c in non-key columns)``."""
        ...
    def mean(self) -> DataFrame:
        """Shortcut for ``.agg(pl.col(c).mean() for c in non-key columns)``."""
        ...
    def min(self) -> DataFrame:
        """Shortcut for ``.agg(pl.col(c).min() for c in non-key columns)``."""
        ...
    def max(self) -> DataFrame:
        """Shortcut for ``.agg(pl.col(c).max() for c in non-key columns)``."""
        ...
    def median(self) -> DataFrame:
        """Shortcut for ``.agg(pl.col(c).median() for c in non-key columns)``."""
        ...
    def n_unique(self) -> DataFrame:
        """Shortcut for ``.agg(pl.col(c).n_unique() for c in non-key columns)``."""
        ...
    def first(self) -> DataFrame:
        """Shortcut for ``.agg(pl.col(c).first() for c in non-key columns)``."""
        ...
    def last(self) -> DataFrame:
        """Shortcut for ``.agg(pl.col(c).last() for c in non-key columns)``."""
        ...
    def count(self) -> DataFrame:
        """Shortcut for ``.agg(pl.col(c).count() for c in non-key columns)``."""
        ...
    def quantile(self, quantile: float, interpolation: Literal["nearest"] = ...) -> DataFrame:
        """Shortcut for ``.agg(pl.col(c).quantile(quantile) for c in non-key columns)``."""
        ...
    def len(self) -> DataFrame:
        """Group sizes, as a two-column DataFrame of the group key(s) plus a ``"len"`` count column."""
        ...
    def map_groups(self, function: Callable[[DataFrame], DataFrame]) -> DataFrame:
        """Apply ``function`` to each group (as a DataFrame), concatenating the returned DataFrames.

        Every group's returned DataFrame must share the same column names.
        """
        ...

class DynamicGroupBy:
    """A dynamic (rolling) time-window view of a DataFrame, produced by ``DataFrame.group_by_dynamic``."""

    def agg(self, *exprs: Expr | str) -> DataFrame:
        """Aggregate each time window; every expression must reduce to a single value.

        Output column order: ``group_by`` key(s) (if any), the window's index
        label column (named after ``index_column``), then the aggregated columns.
        """
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
    def when(self, *predicates: Expr | Any) -> When:
        """Start a conditional expression; multiple predicates are AND-ed together.

        Chain ``.then(value)`` on the result, then optionally more
        ``.when(...).then(...)`` branches, and finish with ``.otherwise(value)``
        or ``.alias(name)`` (unmatched rows are null if omitted).
        """
        ...
    def cov(self, a: Series, b: Series, ddof: int = ...) -> Any:
        """Sample covariance between two Series (eager only — ``a``/``b`` must be ``Series``, not ``Expr``)."""
        ...
    def corr(
        self,
        a: Series,
        b: Series,
        method: Literal["pearson", "spearman"] = ...,
        *,
        ddof: int | None = ...,
        propagate_nans: bool = ...,
    ) -> Any:
        """Correlation coefficient between two Series (eager only). ``ddof``/``propagate_nans`` are accepted for
        Polars API compatibility but not used — both the Pearson and Spearman implementations fix ``ddof=1``
        and drop pairs where either side is null (rather than propagating NaN).
        """
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
