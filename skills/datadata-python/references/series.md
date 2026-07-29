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
| `s.skew(bias=True)` | 样本偏度（`bias=True` 为总体矩估计） |
| `s.kurtosis(fisher=True, bias=True)` | 峰度（`fisher=True` 为超额峰度） |
| `s.mode()` | 最频繁出现的值，返回 `Series`（可能多个） |
| `s.quantile(q, interpolation="nearest")` | 指定分位数的值（`q` 在 0..1），仅支持 `"nearest"` 插值 |

## 滚动窗口（Rolling）

固定大小窗口上的滑窗计算。`weights` 参数未实现，必须传 `None`（默认）。所有 rolling 方法返回 `Series`。

| 方法 | 说明 |
| --- | --- |
| `s.rolling_min(window_size, *, min_samples=None, center=False)` | 滚动最小值 |
| `s.rolling_max(window_size, *, min_samples=None, center=False)` | 滚动最大值 |
| `s.rolling_sum(window_size, *, min_samples=None, center=False)` | 滚动求和 |
| `s.rolling_mean(window_size, *, min_samples=None, center=False)` | 滚动算术平均 |
| `s.rolling_median(window_size, *, min_samples=None, center=False)` | 滚动中位数 |
| `s.rolling_std(window_size, *, min_samples=None, center=False, ddof=1)` | 滚动样本标准差 |
| `s.rolling_var(window_size, *, min_samples=None, center=False, ddof=1)` | 滚动样本方差 |
| `s.rolling_skew(window_size, *, bias=True, min_samples=None, center=False)` | 滚动偏度 |
| `s.rolling_kurtosis(window_size, *, fisher=True, bias=True, min_samples=None, center=False)` | 滚动峰度 |
| `s.rolling_quantile(q, interpolation="nearest", window_size=2, *, min_samples=None, center=False)` | 滚动分位数（仅 `"nearest"` 插值） |
| `s.rolling_map(function, window_size, *, min_samples=None, center=False)` | 对每个窗口调用 `function(Series)`，取其标量返回值 |

```python
# 7 日均值
s.rolling_mean(7)
# 带最小样本数的滚动求和
s.rolling_sum(7, min_samples=3)
```

## 按索引滚动窗口（Rolling By）

基于另一个 Series（通常是时间/排序列，假定升序）的变长窗口。窗口由**时长字符串**（如 `"2d"`、`"1h"`）定义。

| 方法 | 说明 |
| --- | --- |
| `s.rolling_min_by(by, window, *, min_samples=1, closed="right")` | 按索引滚动最小值 |
| `s.rolling_max_by(by, window, *, min_samples=1, closed="right")` | 按索引滚动最大值 |
| `s.rolling_sum_by(by, window, *, min_samples=1, closed="right")` | 按索引滚动求和 |
| `s.rolling_mean_by(by, window, *, min_samples=1, closed="right")` | 按索引滚动算术平均 |
| `s.rolling_median_by(by, window, *, min_samples=1, closed="right")` | 按索引滚动中位数 |
| `s.rolling_std_by(by, window, *, min_samples=1, closed="right", ddof=1)` | 按索引滚动标准差 |
| `s.rolling_var_by(by, window, *, min_samples=1, closed="right", ddof=1)` | 按索引滚动方差 |

`closed` 控制窗口边界开闭：`"left"` / `"right"` / `"both"` / `"none"`，默认 `"right"`。

```python
# 基于时间列的 2 天滚动均值
s.rolling_mean_by(time_series, "2d")
```

## 指数加权移动（EWM）

提供 `com` / `span` / `half_life` / `alpha` **四选一**来指定衰减参数。

| 方法 | 说明 |
| --- | --- |
| `s.ewm_mean(*, com/span/half_life/alpha, adjust=True, min_samples=1, ignore_nulls=True)` | 指数加权移动平均 |
| `s.ewm_sum(*, com/span/half_life/alpha, adjust=True, min_samples=1, ignore_nulls=True)` | 指数加权移动求和 |
| `s.ewm_var(*, com/span/half_life/alpha, adjust=True, min_samples=1, ignore_nulls=True, bias=False)` | 指数加权移动方差 |
| `s.ewm_std(*, com/span/half_life/alpha, adjust=True, min_samples=1, ignore_nulls=True, bias=False)` | 指数加权移动标准差 |

```python
# 跨度 7 的指数加权均值
s.ewm_mean(span=7)
# 半衰期 3 的指数加权标准差
s.ewm_std(half_life=3)
```

## 变换与排序

| 方法 | 说明 |
| --- | --- |
| `s.diff(n=1, null_behavior="ignore")` | 与 `n` 个位置前的值之差（仅支持 `"ignore"`） |
| `s.cum_sum(*, reverse=False)` | 累计求和（`reverse=True` 从末尾反向累加） |
| `s.cum_prod(*, reverse=False)` | 累计乘积 |
| `s.pct_change(n=1)` | 与 `n` 个位置前值的变化百分比，返回 Float64 |
| `s.sort(*, descending=False, nulls_last=False)` | 按值排序（稳定），null 默认排最前 |
| `s.forward_fill(limit=None)` | 用上一个非 null 值填充 null |
| `s.backward_fill(limit=None)` | 用下一个非 null 值填充 null |
| `s.unique(*, maintain_order=False)` | 去重后的值 |
| `s.shift(n=1, *, fill_value=None)` | 移动 `n` 个位置（正数下移），空位填 `fill_value`（默认 null） |
| `s.interpolate(method="linear")` | 线性插值填充 null（仅 `"linear"`） |

## 选取

| 方法 | 说明 |
| --- | --- |
| `s.head(n=5)` | 前 `n` 行（`n` 为负时去掉末尾 `\|n\|` 行） |
| `s.tail(n=5)` | 后 `n` 行（`n` 为负时去掉开头 `\|n\|` 行） |
| `s.slice(offset, length=None)` | 从 `offset`（可为负）起取 `length` 行（`None` 到末尾） |
| `s.gather_every(n, offset=0)` | 每隔 `n` 行取一行，从 `offset` 开始 |
| `s.sample(n=None, *, fraction=None, with_replacement=False, shuffle=False, seed=None)` | 随机采样（`n` 或 `fraction` 二选一） |
| `s.top_k(k=5)` | `k` 个最大值 |
| `s.bottom_k(k=5)` | `k` 个最小值 |

## 映射

| 方法 | 说明 |
| --- | --- |
| `s.replace_strict(old, new, *, default=None, return_dtype=None)` | 严格替换：在 `old` 中找到的值替换为 `new` 中对应位置的值，未找到的变为 `default` |
| `s.value_counts(*, sort=False, name=None, normalize=False)` | 值频次统计，返回两列 `DataFrame`（值列 + `"count"` 列） |
| `s.map_elements(function, return_dtype=None, skip_nulls=True)` | 对每个元素调用 Python 回调，返回新 Series |

```python
# 元素级映射
s.map_elements(lambda x: x * 2 if isinstance(x, (int, float)) else x)
# 值频次
s.value_counts(sort=True)
```

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
