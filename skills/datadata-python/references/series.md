# Series

`Series` 是一个**即时求值**的、单一类型的列。它是 [`DataFrame`](./dataframe.md) 的组成单元，也可作为 `main()` 的返回值（转换为单列结果集）。签名以 [`__builtins__.pyi`](./__builtins__.pyi) 为准。

与惰性的 [`Expr`](./expr.md) 不同，`Series` 上的运算会**立即计算**出结果。

## 构造

```python
Series(name, values=None, dtype=None, *, strict=True, nan_to_null=False)
# 或省略名称
Series(values, name=None, dtype=None)
```

```python
Series("value", [10, 20, 30])
Series([1.0, 2.0, 3.0], name="price")
```

## 属性

| 属性 | 类型 | 说明 |
| --- | --- | --- |
| `name` | `str` | 列名（未指定时默认为 `"series"`） |
| `dtype` | `DataType` | 逻辑数据类型 |

## 转换与清洗

| 方法 | 说明 |
| --- | --- |
| `s.to_list()` | 转为 Python `list`（null → `None`） |
| `s.cast(dtype)` | 转换 dtype（严格模式，失败抛异常） |
| `s.abs()` | 逐元素绝对值 |
| `s.round(ndigits=0)` | 四舍五入到 `ndigits` 位小数 |
| `s.fill_null(value)` | 用标量 `value` 替换 null（`None` 为空操作） |
| `s.is_null()` / `s.is_not_null()` | 返回标记 null / 非 null 的布尔 Series |
| `s.filter(mask)` | 按布尔 `mask` Series 保留元素 |
| `s.alias(name)` / `s.rename(name)` | 返回重命名后的副本 |

## 聚合

以下方法返回单个标量值：

| 方法 | 说明 |
| --- | --- |
| `s.sum()` | 所有非 null 值之和 |
| `s.mean()` | 算术平均 |
| `s.min()` / `s.max()` | 最小 / 最大非 null 值 |
| `s.median()` | 中位数 |
| `s.std()` / `s.var()` | 样本标准差 / 方差 |
| `s.count()` | 非 null 值个数 |
| `s.n_unique()` | 不同值个数（null 记为一个不同值） |
| `s.first()` / `s.last()` | 首个 / 末尾值 |

## 索引与长度

```python
len(s)      # 元素个数
s[0]        # 取指定位置的值（支持负索引）
```

## 运算符

`Series` 重载了完整的算术、比较、逻辑运算符，均返回新的 `Series`：

- 算术：`+` `-` `*` `/` `//` `%` `**`
- 比较：`==` `!=` `<` `<=` `>` `>=`（返回布尔 Series）
- 逻辑：`&` `|` `~`

```python
def main():
    s = Series("value", [1, -2, 3, -4])
    positive = s.filter(s > 0)   # 比较得到布尔 mask，再过滤
    return positive              # Series([1, 3])
```
