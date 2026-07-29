# Expr 表达式

`Expr` 是一个**惰性、可组合的列表达式**，由 `pl.col(name)` 或 `pl.lit(value)` 构建，在 `DataFrame` 的 `select` / `with_columns` / `filter` 以及 `GroupBy.agg` 中被求值。签名以 [`__builtins__.pyi`](./__builtins__.pyi) 为准。

```python
pl.col("amount")                        # 引用列
pl.col("amount") * 1.1                   # 运算得到新表达式
pl.col("amount").sum().alias("total")    # 聚合并重命名
```

> **比较运算返回 Expr**：与普通 Python 语义不同，对 `Expr` 使用比较运算符会构建一个**惰性布尔表达式并返回 `Expr`**，而**不是** `bool`。因此 `pl.col("a") > 5` 是一个表达式，可直接用于 `filter`。

## 通用方法

| 方法 | 说明 |
| --- | --- |
| `e.alias(name)` | 重命名该表达式产出的列 |
| `e.cast(dtype)` | 将结果转换为另一 dtype |
| `e.is_null()` / `e.is_not_null()` | 每个值是否为 null / 非 null |
| `e.fill_null(value)` | 用表达式或标量替换 null |
| `e.is_in(values)` | 每个值是否属于 `values` 序列 |
| `e.abs()` | 逐元素绝对值 |
| `e.round(ndigits=0)` | 四舍五入到 `ndigits` 位小数 |

## 聚合方法

在 `GroupBy.agg` 或对整列求值时，将一列归约为单个值：

| 方法 | 说明 |
| --- | --- |
| `e.sum()` | 非 null 值之和 |
| `e.mean()` | 算术平均 |
| `e.min()` / `e.max()` | 最小 / 最大值 |
| `e.median()` | 中位数 |
| `e.std()` / `e.var()` | 样本标准差 / 方差 |
| `e.count()` | 非 null 值个数 |
| `e.n_unique()` | 不同值个数 |
| `e.first()` / `e.last()` | 首个 / 末尾值 |
| `e.skew(bias=True)` | 样本偏度 |
| `e.kurtosis(fisher=True, bias=True)` | 峰度（`fisher=True` 为超额峰度） |
| `e.mode()` | 最频繁出现的值 |
| `e.quantile(q, interpolation="nearest")` | 指定分位数的值（仅 `"nearest"` 插值） |

## 滚动窗口（Rolling）

固定大小窗口上的滑窗计算，在 `select` / `with_columns` / `agg` 中求值。`weights` 未实现，必须传 `None`（默认）。

| 方法 | 说明 |
| --- | --- |
| `e.rolling_min(window_size, *, min_samples=None, center=False)` | 滚动最小值 |
| `e.rolling_max(window_size, *, min_samples=None, center=False)` | 滚动最大值 |
| `e.rolling_sum(window_size, *, min_samples=None, center=False)` | 滚动求和 |
| `e.rolling_mean(window_size, *, min_samples=None, center=False)` | 滚动算术平均 |
| `e.rolling_median(window_size, *, min_samples=None, center=False)` | 滚动中位数 |
| `e.rolling_std(window_size, *, min_samples=None, center=False, ddof=1)` | 滚动标准差 |
| `e.rolling_var(window_size, *, min_samples=None, center=False, ddof=1)` | 滚动方差 |
| `e.rolling_skew(window_size, *, bias=True, min_samples=None, center=False)` | 滚动偏度 |
| `e.rolling_kurtosis(window_size, *, fisher=True, bias=True, min_samples=None, center=False)` | 滚动峰度 |
| `e.rolling_quantile(q, interpolation="nearest", window_size=2, *, min_samples=None, center=False)` | 滚动分位数 |
| `e.rolling_map(function, window_size, *, min_samples=None, center=False)` | 对每个窗口调用 `function(Series)`，取标量返回值 |

## 按索引滚动窗口（Rolling By）

基于 `by`（列名或表达式，假定升序）的变长窗口，窗口由时长字符串定义。

| 方法 | 说明 |
| --- | --- |
| `e.rolling_min_by(by, window, *, min_samples=1, closed="right")` | 按索引滚动最小值 |
| `e.rolling_max_by(by, window, *, min_samples=1, closed="right")` | 按索引滚动最大值 |
| `e.rolling_sum_by(by, window, *, min_samples=1, closed="right")` | 按索引滚动求和 |
| `e.rolling_mean_by(by, window, *, min_samples=1, closed="right")` | 按索引滚动算术平均 |
| `e.rolling_median_by(by, window, *, min_samples=1, closed="right")` | 按索引滚动中位数 |
| `e.rolling_std_by(by, window, *, min_samples=1, closed="right", ddof=1)` | 按索引滚动标准差 |
| `e.rolling_var_by(by, window, *, min_samples=1, closed="right", ddof=1)` | 按索引滚动方差 |

> **注意**：Expr 的 `*_by` 方法中 `by` 参数可以是 `str`（列名）或 `Expr`；Series 的 `*_by` 方法中 `by` 必须是 `Series`。

## 指数加权移动（EWM）

提供 `com` / `span` / `half_life` / `alpha` **四选一**。

| 方法 | 说明 |
| --- | --- |
| `e.ewm_mean(*, com/span/half_life/alpha, adjust=True, min_samples=1, ignore_nulls=True)` | 指数加权移动平均 |
| `e.ewm_sum(*, ..., same params)` | 指数加权移动求和 |
| `e.ewm_var(*, ..., bias=False)` | 指数加权移动方差 |
| `e.ewm_std(*, ..., bias=False)` | 指数加权移动标准差 |

## 变换与排序

| 方法 | 说明 |
| --- | --- |
| `e.diff(n=1, null_behavior="ignore")` | 与 `n` 个位置前的值之差 |
| `e.cum_sum(*, reverse=False)` | 累计求和 |
| `e.cum_prod(*, reverse=False)` | 累计乘积 |
| `e.pct_change(n=1)` | 变化百分比，返回 Float64 |
| `e.sort(*, descending=False, nulls_last=False)` | 按值排序（稳定） |
| `e.forward_fill(limit=None)` | 用上一个非 null 值填充 null |
| `e.backward_fill(limit=None)` | 用下一个非 null 值填充 null |
| `e.unique(*, maintain_order=False)` | 去重后的值 |
| `e.shift(n=1, *, fill_value=None)` | 移动 `n` 个位置，空位填 `fill_value` |
| `e.interpolate(method="linear")` | 线性插值填充 null（仅 `"linear"`） |
| `e.top_k(k=5)` | `k` 个最大值 |
| `e.bottom_k(k=5)` | `k` 个最小值 |
| `e.replace_strict(old, new, *, default=None, return_dtype=None)` | 严格值替换 |

## 窗口函数 `over`

```python
e.over(*partition_by, mapping_strategy="group_to_rows") -> Expr
```

按 `partition_by`（一个或多个列名/表达式）分区求值，然后将每个分区的结果广播回原始行。至少需要一个分区列；仅支持 `mapping_strategy="group_to_rows"`。

```python
# 每个类别内部的金额排名（以降序排序即排名）
df.with_columns(
    pl.col("amount").sort(descending=True).over("category").alias("rank_in_category")
)
# 每行值占所在类别总额的比例
df.with_columns(
    (pl.col("amount") / pl.col("amount").sum().over("category")).alias("pct_of_category")
)
```

## 元素级映射 `map_elements`

```python
e.map_elements(function, return_dtype=None, skip_nulls=True) -> Expr
```

对每个元素应用 Python 回调，返回新表达式。`skip_nulls=True`（默认）跳过 null 不调用回调，输出仍为 null。`return_dtype` 未指定时从回调结果自动推断。

```python
df.with_columns(
    pl.col("score").map_elements(lambda x: "A" if x >= 90 else "B").alias("grade")
)
```

## 条件表达式 `pl.when` / `When` / `Then`

`pl.when(*predicates)` → `When` → `.then(value)` → `Then` → `.when(...)` / `.otherwise(value)` / `.alias(name)`

```python
# when/then/otherwise 链式构建条件列
df.with_columns(
    pl.when(pl.col("amount") > 100).then(pl.lit("high"))
      .when(pl.col("amount") > 50).then(pl.lit("mid"))
      .otherwise(pl.lit("low"))
      .alias("level")
)

# 不调 .otherwise() 时，未匹配的行填 null
df.with_columns(
    pl.when(pl.col("amount") > 100).then(pl.lit("flagged")).alias("flag")
)
```

## 运算符

- 算术：`+` `-` `*` `/` `//` `%` `**`，以及一元 `-`（取负）
- 比较：`==` `!=` `<` `<=` `>` `>=`（构建布尔表达式）
- 逻辑：`&` `|` `~`

## 字符串命名空间 `.str`

通过 `e.str` 访问字符串操作（仅 `Expr` 提供，`Series` 上不可用）：

| 方法 | 说明 |
| --- | --- |
| `.str.contains(pat)` | 是否包含子串 `pat` |
| `.str.starts_with(pat)` / `.str.ends_with(pat)` | 是否以 `pat` 开头 / 结尾 |
| `.str.to_uppercase()` / `.str.to_lowercase()` | 大写 / 小写 |
| `.str.strip_chars(chars=None)` | 去除首尾空白，或指定的 `chars` |
| `.str.replace(old, new)` | 替换**首个**匹配 |
| `.str.replace_all(old, new)` | 替换**所有**匹配 |
| `.str.len_chars()` | 字符数 |
| `.str.slice(offset, length=None)` | 从 `offset` 起切 `length` 个字符 |
| `.str.to_datetime(format=None)` | 解析为 Datetime，可选显式 `format` |
| `.str.to_date(format=None)` | 解析为 Date，可选显式 `format` |

```python
# 将 SQL 返回的字符串时间列转为 Datetime，再提取年份
df.with_columns(
    pl.col("created_at").str.to_datetime().dt.year().alias("year")
)
```

## 日期时间命名空间 `.dt`

通过 `e.dt` 访问日期时间操作（仅 `Expr` 提供）：

| 方法 | 说明 |
| --- | --- |
| `.dt.year()` / `.dt.month()` / `.dt.day()` | 提取年 / 月 / 日 |
| `.dt.hour()` / `.dt.minute()` / `.dt.second()` | 提取时 / 分 / 秒 |
| `.dt.weekday()` | ISO 星期几 |
| `.dt.truncate(every)` | 截断到时间桶边界（如 `"1mo"`、`"1d"`） |
| `.dt.strftime(format)` | 按 `strftime` 风格格式化为字符串 |

```python
# 按月汇总
df.group_by(pl.col("created_at").dt.truncate("1mo").alias("month")).agg(
    pl.col("amount").sum().alias("total")
)
```
