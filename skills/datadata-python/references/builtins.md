# 全局函数与命名空间

以下名称已注入 Python 脚本作用域，**无需 `import`** 即可使用。签名以 [`__builtins__.pyi`](./__builtins__.pyi) 为准。

## query

```python
query(sql: str, *args) -> DataFrame
```

对已绑定 / 挂载的数据源执行 SQL 查询，返回结果的 `DataFrame`。走的是与普通 SQL 查询相同的查询引擎通路，支持多数据源与跨源查询。

```python
def main():
    df = query("SELECT id, name, amount FROM orders WHERE amount > ?", 100)
    return df
```

- 位置参数 `*args` 依次替换 SQL 中的 `?` 占位符（参数化查询）。
- **时间列注意**：SQL 返回的 timestamp / date 列会以**字符串**形式回来，需用 `.str.to_datetime()` 或 `.str.to_date()` 转换后才能做日期运算：

  ```python
  df = df.with_columns(pl.col("created_at").str.to_datetime())
  ```

## fetch

```python
fetch(url: str, method="GET", body=None, headers=None, timeout=30) -> Response
```

发起 HTTP 请求，返回 `Response`。JS `fetch` 风格封装。

```python
def main():
    res = fetch(
        "https://api.example.com/items",
        method="POST",
        body={"page": 1},
        headers={"Authorization": "Bearer ..."},
    )
    if not res.ok:
        return [{"error": res.status}]
    return res.json()
```

**参数**

| 参数 | 说明 |
| --- | --- |
| `url` | 请求地址 |
| `method` | HTTP 方法，默认 `"GET"` |
| `body` | 请求体；为 `dict` / `list` 时自动 JSON 序列化，并在未显式指定时默认 `content-type: application/json`；已是 `str` 则原样发送 |
| `headers` | 请求头 `dict` |
| `timeout` | 超时秒数，默认 `30` |

**错误处理**

- **传输层错误**（DNS / 连接失败等）会抛出可捕获的异常，用 `try/except` 处理。
- **HTTP 4xx / 5xx 状态码不会抛异常**，需通过 `res.ok` / `res.status` 判断。

**Response 对象**

| 成员 | 说明 |
| --- | --- |
| `res.ok` | 布尔，状态码是否为 2xx |
| `res.status` | HTTP 状态码（int） |
| `res.status_text` | 状态描述文本 |
| `res.headers.get(name, default=None)` | 按名称读响应头（大小写不敏感） |
| `res.text()` | 响应体原始字符串 |
| `res.json()` | 将响应体解析为 JSON |

> `fetch()` 仅用于访问**外部 HTTP 服务**。

## args

```python
args: dict
```

调用方传入的脚本参数，**始终是一个 `dict`**。

```python
def main():
    threshold = args["threshold"]
    return query("SELECT * FROM sales").filter(pl.col("revenue") > threshold)
```

## print

```python
print(*values)
```

`print()` 被重定向到**脚本日志**，输出不会进入结果集，便于调试。

```python
def main():
    df = query("SELECT * FROM orders")
    print("行数:", df.height)
    return df
```

## pl 命名空间

`pl` 提供表达式构造器、数据类型常量，以及 `DataFrame` / `Series` 类型。

| 成员 | 说明 |
| --- | --- |
| `pl.col(name)` | 按列名引用一个列，返回 [`Expr`](./expr.md) |
| `pl.lit(value)` | 由标量构造字面量表达式，返回 [`Expr`](./expr.md) |
| `pl.DataFrame` | [`DataFrame`](./dataframe.md) 类型（与全局 `DataFrame` 等价） |
| `pl.Series` | [`Series`](./series.md) 类型（与全局 `Series` 等价） |
| `pl.Int` / `pl.Float` / `pl.Boolean` / `pl.String` / `pl.Datetime` / `pl.Date` | 数据类型常量 |

```python
def main():
    df = query("SELECT category, amount FROM sales")
    return df.with_columns((pl.col("amount") * pl.lit(1.1)).alias("amount_with_tax"))
```

## 数据类型（DataType）

`pl` 命名空间下的逻辑数据类型常量：

| 常量 | 说明 |
| --- | --- |
| `pl.Int` / `pl.Int32` / `pl.Int64` | 整数（物理上均为 Int64，`repr` 为 `Int`） |
| `pl.Float` / `pl.Float32` / `pl.Float64` | 浮点数（物理上均为 Float64，`repr` 为 `Float`） |
| `pl.Boolean` | 布尔 |
| `pl.String` | 字符串 |
| `pl.Datetime` | 日期时间 |
| `pl.Date` | 日期 |

精度在用户侧不作区分：`pl.Int32 == pl.Int64`、`pl.Float32 == pl.Float64` 均成立。用于 `cast()`：

```python
df.select(pl.col("a").cast(pl.Float))
```
