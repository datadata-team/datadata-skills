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
