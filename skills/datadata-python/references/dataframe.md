# DataFrame

`DataFrame` 是二维、列式的表结构，由多个等长的 [`Series`](./series.md) 组成。`query()` 返回 `DataFrame`，它也是 `main()` 推荐的返回类型。签名以 [`__builtins__.pyi`](./__builtins__.pyi) 为准。

## 构造

```python
DataFrame(data=None, schema=None, *, orient=None)
```

`data` 支持多种形态：

```python
# 行式：list[dict]
DataFrame([{"a": 1, "b": "x"}, {"a": 2, "b": "y"}])

# 列式：dict[str, list]
DataFrame({"a": [1, 2], "b": ["x", "y"]})

# 由 Series 组成
DataFrame([Series("a", [1, 2]), Series("b", ["x", "y"])])
```

- `schema` — 可选，指定列名与 dtype，形如 `{"a": pl.Int, "b": pl.String}` 或列名列表。
- `orient` — `"row"` 或 `"col"`，当 `data` 为嵌套列表时用于指定方向。

## 属性

| 属性 | 类型 | 说明 |
| --- | --- | --- |
| `columns` | `list[str]` | 列名（按顺序） |
| `dtypes` | `list[DataType]` | 每列的 dtype（按列序） |
| `schema` | `dict[str, DataType]` | 列名到 dtype 的映射 |
| `shape` | `tuple[int, int]` | `(行数, 列数)` |
| `height` | `int` | 行数 |
| `width` | `int` | 列数 |

## 选取

| 方法 | 说明 |
| --- | --- |
| `df.head(n=5)` | 前 `n` 行（`n` 为负时去掉末尾 `\|n\|` 行） |
| `df.tail(n=5)` | 后 `n` 行（`n` 为负时去掉开头 `\|n\|` 行） |
| `df.limit(n=5)` | `head` 的别名 |
| `df.slice(offset, length=None)` | 从 `offset`（可为负）起取 `length` 行（`None` 到末尾） |
| `df.gather_every(n, offset=0)` | 每隔 `n` 行取一行 |
| `df.sample(n=None, *, fraction=None, with_replacement=False, shuffle=False, seed=None)` | 随机采样（`n` 或 `fraction` 二选一） |
| `df.is_empty()` | 是否为零行 |

## 变换

| 方法 | 说明 |
| --- | --- |
| `df.unique(subset=None, *, keep="first", maintain_order=False)` | 按 `subset` 列去重（默认全部列）；`keep` 可选 `"first"` / `"last"` / `"any"` / `"none"` |
| `df.n_unique(subset=None)` | 不同行数（按 `subset` 列比较，默认全部列） |
| `df.sort(by, *, descending=False, nulls_last=False)` | 按一列或多列排序（稳定）；`descending` / `nulls_last` 可以是单个 bool 或与 `by` 等长的列表 |
| `df.shift(n=1, *, fill_value=None)` | 所有列移动 `n` 个位置，空位填 `fill_value`（默认 null） |

### 整表聚合（缩为单行）

以下方法对每列独立求值，结果缩为一行。不支持聚合的列（如字符串）结果为 null。

| 方法 | 说明 |
| --- | --- |
| `df.sum()` | 每列求和 |
| `df.mean()` | 每列算术平均 |
| `df.min()` / `df.max()` | 每列最小 / 最大值 |
| `df.median()` | 每列中位数 |
| `df.std()` / `df.var()` | 每列样本标准差 / 方差 |
| `df.count()` | 每列非 null 计数 |

### select

```python
df.select(*exprs: Expr | str) -> DataFrame
```
对表达式（或裸列名字符串）求值，生成一个新的 DataFrame（仅包含所选列）。

```python
df.select(pl.col("name"), (pl.col("amount") * 2).alias("double"))
```

### with_columns

```python
df.with_columns(*exprs: Expr | str) -> DataFrame
```
新增或覆盖列，同时保留所有已有列。

```python
df.with_columns(pl.col("created_at").str.to_datetime())
```

### filter

```python
df.filter(predicate: Expr | str) -> DataFrame
```
仅保留 `predicate`（一个布尔 [`Expr`](./expr.md)）为真的行。

```python
df.filter(pl.col("amount") > 500)
```

### group_by

```python
df.group_by(*keys: str) -> GroupBy
```
按一个或多个列名分组，返回 `GroupBy` 视图（配合 `.agg()` 使用）。

```python
df.group_by("category", "region").agg(pl.col("amount").sum().alias("total"))
```

### group_by_dynamic（时间窗口分组）

```python
df.group_by_dynamic(
    index_column: str,
    *,
    every: str,
    period: str | None = None,
    offset: str | None = None,
    closed: Literal["left", "right", "both", "none"] = "left",
    label: Literal["left", "right", "datapoint"] = "left",
    group_by: str | Sequence[str] | None = None,
    start_by: Literal["window"] = "window",
) -> DynamicGroupBy
```

对 `index_column`（必须是 Datetime 或 Date）做动态（滚动）时间窗口分组。

- `every` — 窗口步长（如 `"2d"`、`"1h"`）
- `period` — 窗口宽度，默认等于 `every`（滚动窗口）
- `offset` — 窗口边界偏移量
- `closed` — 窗口边界开闭，默认 `"left"`
- `label` — 输出中用哪个边界作为窗口索引值
- `group_by` — 额外按键列分组后再开窗
- 仅支持 `start_by="window"`

```python
# 按 7 天滚动窗口聚合
df.group_by_dynamic("date", every="7d").agg(
    pl.col("amount").sum().alias("weekly_total")
)
# 带分组键的 1 天窗口
df.group_by_dynamic("ts", every="1d", group_by="sensor_id").agg(
    pl.col("reading").mean().alias("daily_avg")
)
```

### upsample

```python
df.upsample(time_column, *, every, group_by=None, maintain_order=False) -> DataFrame
```

在 `time_column`（Datetime 或 Date）上按 `every` 步长补全缺失的时间网格点。缺失行的其他列填 null，之后可用 `forward_fill` / `backward_fill` 填充。`group_by` 按分组键独立补全网格。

```python
# 补全到小时级网格，前向填充
df.upsample("ts", every="1h").with_columns(
    pl.col("value").forward_fill()
)
```

## Join

### 等值 join

```python
df.join(
    other: DataFrame,
    on=None,              # 两边同名的 key
    how="inner",          # inner / left / right / full / cross / semi / anti
    *,
    left_on=None,         # 左边 key（与 right_on 搭配）
    right_on=None,        # 右边 key（与 left_on 搭配）
    suffix="_right",      # 非 key 列重名时的后缀
    nulls_equal=False,    # null key 是否匹配
    coalesce=None,        # 合并 key 列（默认除 "full" 外均为 True）
) -> DataFrame
```

`on` 和 `left_on`/`right_on` 二选一。`how="outer"` 是 `"full"` 的别名。`how="cross"` 不需要 key。

```python
# 内连接
df_a.join(df_b, on="id")
# 左连接，不同 key 名
df_a.join(df_b, left_on="a_id", right_on="b_id", how="left")
# 反连接：左表中 key 不在右表的行
df_a.join(df_b, on="id", how="anti")
```

### 非等值 join

```python
df.join_where(other: DataFrame, *predicates: Expr, suffix="_right") -> DataFrame
```

内连接，按任意（非等值）谓词表达式 AND 匹配。内部先做笛卡尔积再过滤。

```python
# 区间匹配
df_a.join_where(df_b, pl.col("a.value") >= pl.col("b.low"), pl.col("a.value") < pl.col("b.high"))
```

### 最近匹配 join（asof）

```python
df.join_asof(
    other: DataFrame,
    *,
    on=None,              # 两边同名的 key
    left_on=None,         # 左边 key（与 right_on 二选一或搭配 on）
    right_on=None,
    by=None,              # 精确匹配的分组 key（两边同名）
    by_left=None,         # 左边分组 key
    by_right=None,        # 右边分组 key
    strategy="backward",  # backward / forward / nearest
    suffix="_right",
    tolerance=None,       # 匹配容差（数值或时长字符串如 "1d"）
    allow_exact_matches=True,
    coalesce=True,
) -> DataFrame
```

按最近 key 值匹配，类似 Polars 的 asof join。`strategy` 控制匹配方向。

```python
# 按时间戳做最近匹配
df_a.join_asof(df_b, on="ts", strategy="backward", tolerance="1h")
```

## 导出

| 方法 | 返回 | 说明 |
| --- | --- | --- |
| `df.to_dicts()` | `list[dict]` | 转为行 dict 列表 |
| `df.rows()` | `list[tuple]` | 转为行元组列表 |
| `df.to_dict()` | `dict[str, list]` | 转为「列名 → 值列表」 |
| `df.get_column(name)` | `Series` | 按列名取单列 |
| `df[name]` | `Series` | 按列名取单列（列不存在抛 `KeyError`） |
| `len(df)` | `int` | 行数（等价于 `height`） |

## GroupBy

由 `DataFrame.group_by(...)` 产生的分组视图。

### agg

```python
gb.agg(*exprs: Expr | str) -> DataFrame
```
对每个分组做聚合，每个表达式必须归约为单个值。

```python
df.group_by("category").agg(
    pl.col("amount").sum().alias("total"),
    pl.col("amount").mean().alias("avg"),
    pl.col("id").n_unique().alias("orders"),
)
```

### 快捷聚合

以下方法等价于对所有非 key 列做对应聚合的 `.agg()`：

| 方法 | 说明 |
| --- | --- |
| `gb.sum()` | 每列求和 |
| `gb.mean()` | 每列算术平均 |
| `gb.min()` / `gb.max()` | 每列最小 / 最大值 |
| `gb.median()` | 每列中位数 |
| `gb.n_unique()` | 每列不同值个数 |
| `gb.first()` / `gb.last()` | 每列首个 / 末尾值 |
| `gb.count()` | 每列非 null 计数 |
| `gb.quantile(q, interpolation="nearest")` | 每列指定分位数 |

### len

```python
gb.len() -> DataFrame
```
分组行数，返回「key 列 + `"len"` 计数列」的两列 DataFrame。

### map_groups

```python
gb.map_groups(function: Callable[[DataFrame], DataFrame]) -> DataFrame
```
对每个分组调用 `function`（入参为子 DataFrame），拼接返回的 DataFrame。每个分组的返回值必须列名一致。

```python
# 每组取金额最大的 2 行
df.group_by("category").map_groups(lambda g: g.sort("amount", descending=True).head(2))
```

## DynamicGroupBy

由 `DataFrame.group_by_dynamic(...)` 产生的时间窗口分组视图。

```python
dg.agg(*exprs: Expr | str) -> DataFrame
```

对每个时间窗口做聚合。输出列序：`group_by` key 列（如有）、窗口索引标签列（名为 `index_column`）、聚合结果列。

```python
df.group_by_dynamic("ts", every="1d").agg(
    pl.col("value").mean().alias("daily_avg"),
    pl.col("value").max().alias("daily_max"),
)
```
