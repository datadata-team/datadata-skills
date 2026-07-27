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

## 方法

### is_empty

```python
df.is_empty() -> bool
```
DataFrame 是否为零行。

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

### 导出

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
