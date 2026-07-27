# 示例合集

以下示例覆盖 Python 查询脚本的全部特性，**每一条都已在真实执行器上跑通验证**。所有脚本都以定义 `main()` 为入口，`main()` 的返回值即查询结果。

## 返回值的四种形态

`main()` 可返回 `DataFrame` / `Series` / `list[dict]` / `dict[str, list]`（列式）。

### 返回 `list[dict]`

```python
def main():
    return [{"city": "北京", "value": 1}, {"city": "上海", "value": 2}]
```

结果：`city(string), value(bigint)` → `北京,1` / `上海,2`

### 返回 `DataFrame`

```python
def main():
    return DataFrame([{"a": 1, "b": "x"}, {"a": 2, "b": "y"}])
```

结果：`a(bigint), b(string)` → `1,x` / `2,y`

### 返回 `Series`

```python
def main():
    return Series("value", [10, 20, 30])
```

结果：`value(bigint)` → `10` / `20` / `30`

### 返回 `dict[str, list]`（列式）

键是列名，值是等长的列表：

```python
def main():
    return {"city": ["北京", "上海"], "value": [1, 2]}
```

结果：`city(string), value(bigint)` → `北京,1` / `上海,2`

> 若要返回若干标量汇总值，请包成**单行 list[dict]**（见下方「Series 聚合」示例），顶层 dict 只支持列式 `dict[str, list]`。

## 使用参数 `args`

调用方传入的参数通过全局 `args`（始终是 dict）读取：

```python
def main():
    return [{"threshold": args["threshold"], "label": args["label"]}]
```

以 `{"threshold": 500, "label": "hi"}` 调用时，结果：`threshold(bigint), label(string)` → `500,hi`

## 从数据源取数 `query`

```python
def main():
    return query("SELECT id, name FROM users")
```

结果（示例数据）：`id(bigint), name(string)` → `1,alice` / `2,bob`

带占位符参数：

```python
def main():
    return query("SELECT * FROM orders WHERE amount > ?", 100)
```

### 处理时间列

`query()` 返回的时间列是**字符串**，需先 `.str.to_datetime()` 转换，之后才能用 `.dt`：

```python
def main():
    df = query("SELECT created_at, amount FROM orders")
    df = df.with_columns(pl.col("created_at").str.to_datetime())
    return df.with_columns(pl.col("created_at").dt.year().alias("year"))
```

结果（示例数据）：`created_at(timestamp), amount(bigint), year(bigint)` → `2026-01-15 10:00:00, 100, 2026`

## HTTP 请求 `fetch`

### GET + 解析 JSON

```python
def main():
    res = fetch("https://api.example.com/users")
    if not res.ok:
        return [{"error": res.status}]
    return res.json()
```

当接口返回 `[{"id":1,"name":"a"},{"id":2,"name":"b"}]` 时，结果：`id(bigint), name(string)` → `1,a` / `2,b`

### POST + dict body 自动 JSON 序列化

```python
def main():
    res = fetch("https://api.example.com/query", method="POST", body={"page": 1, "size": 100})
    return res.json()
```

`body` 为 dict 时自动序列化为 `{"page": 1, "size": 100}`，并默认带上 `content-type: application/json`。

## 数据处理（Polars 风格）

### select / with_columns / filter

```python
def main():
    df = DataFrame([
        {"category": "a", "amount": 100},
        {"category": "b", "amount": 600},
        {"category": "a", "amount": 50},
    ])
    return (df
        .filter(pl.col("amount") > 80)
        .with_columns((pl.col("amount") * 1.1).round(2).alias("taxed"))
        .select("category", "amount", "taxed"))
```

结果：`category(string), amount(bigint), taxed(float)` → `a,100,110` / `b,600,660`

### 分组聚合 group_by().agg()

```python
def main():
    df = DataFrame([
        {"cat": "a", "amt": 100},
        {"cat": "b", "amt": 600},
        {"cat": "a", "amt": 50},
    ])
    return df.group_by("cat").agg(
        pl.col("amt").sum().alias("total"),
        pl.col("amt").count().alias("n"),
    )
```

结果：`cat(string), total(bigint), n(bigint)` → `a,150,2` / `b,600,1`

### DataFrame 导出

```python
def main():
    df = DataFrame([{"a": 1, "b": "x"}, {"a": 2, "b": "y"}])
    return df.to_dicts()
```

结果：`a(bigint), b(string)` → `1,x` / `2,y`

## Series 操作

即时求值的单列，比较运算得到布尔 mask 用于过滤；标量结果包成单行 list[dict] 返回：

```python
def main():
    s = Series("v", [1, -2, 3, -4])
    pos = s.filter(s > 0)
    return [{"total": s.sum(), "positive_count": len(pos.to_list())}]
```

结果：`total(bigint), positive_count(bigint)` → `-2,2`

## 表达式 Expr

### 字符串命名空间 .str

```python
def main():
    df = DataFrame([{"name": "alice"}, {"name": "bob"}])
    return df.with_columns(pl.col("name").str.to_uppercase().alias("upper"))
```

结果：`name(string), upper(string)` → `alice,ALICE` / `bob,BOB`

### 日期时间命名空间 .dt

```python
def main():
    df = DataFrame([{"d": "2026-01-15"}, {"d": "2026-03-20"}])
    return df.with_columns(pl.col("d").str.to_datetime().dt.year().alias("year"))
```

结果：`d(string), year(bigint)` → `2026-01-15, 2026` / `2026-03-20, 2026`

### 聚合 + pl.lit + cast

```python
def main():
    df = DataFrame([{"a": 1}, {"a": 2}, {"a": 3}])
    return df.select((pl.col("a").cast(pl.Float) * pl.lit(2)).alias("doubled"))
```

结果：`doubled(float)` → `2` / `4` / `6`

## 打印日志 print

```python
def main():
    df = DataFrame([{"a": 1}, {"a": 2}])
    print("height:", df.height)
    return df
```

结果：`a(bigint)` → `1` / `2`；脚本日志：`height: 2`

## 使用标准库

冻结的纯 Python 标准库与常用原生模块均可 `import`：

```python
import json, re, math, datetime, hashlib

def main():
    return [{
        "j": json.dumps({"x": 1}),
        "re_ok": bool(re.match(r"\d+", "123")),
        "ceil": math.ceil(1.2),
        "year": datetime.date(2026, 7, 27).year,
        "sha8": hashlib.sha256(b"a").hexdigest()[:8],
    }]
```

结果：`j(string), re_ok(boolean), ceil(bigint), year(bigint), sha8(string)` → `{"x": 1}, true, 2, 2026, ca978112`
