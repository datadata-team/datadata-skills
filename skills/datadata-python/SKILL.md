---
name: datadata-python
description: |
  本技能包含了 Datadata Python 查询脚本的完整参考文档，当编写 Datadata Python 查询脚本时，**必须先加载本技能**。
  Write Python data query scripts for the Datadata platform — real Python (RustPython/WASM sandbox) with a Polars-style DataFrame/Series/Expr API, SQL data access via query(), and HTTP requests via fetch(). Use when the user needs to write data transformation, data cleaning, data generation, or custom data processing logic in Python.
---

# Datadata Python 查询脚本编写

Python 查询脚本是 Datadata 平台与 SQL、DQL 并列的第三种查询脚本类型。它运行**真正的 Python**（RustPython 编译为 WebAssembly，在沙箱中执行），提供 **Polars 风格**的 `DataFrame` / `Series` / `Expr` 数据处理 API，并内置 SQL 取数（`query()`）与 HTTP 请求（`fetch()`）能力。

## 🔴 核心规则

### 1. 脚本必须定义 `main()` 函数

Python 脚本**必须定义一个可调用的 `main()` 函数**作为入口，`main()` 的返回值即查询结果。没有 `main()` 会直接报错。

```python
# ✅ 正确
def main():
    df = query("SELECT * FROM users")
    return df

# ❌ 错误：没有 main()，无法执行
df = query("SELECT * FROM users")
```

`main()` 可返回以下形态之一：

- `DataFrame` — 直接转换为结果集（推荐）
- `Series` — 转换为单列结果集
- `list[dict]` — 每个 dict 是一行
- `dict[str, list]` — **列式**，键是列名、值是等长的列表

> 若要返回若干标量汇总值，**包成单行 `list[dict]`**（如 `return [{'total': total, 'count': n}]`），因为顶层 dict 仅支持 `dict[str, list]` 列式形态。

### 2. 编写前必须先阅读对应的 References 文档

**禁止仅凭本文档就编写代码。** 本文档只是索引，实际 API 签名、参数、返回值以 references 为准。

| 场景 | 必读文档 |
| --- | --- |
| SQL 取数 / HTTP 请求 / 参数 / 日志 | [builtins.md](./references/builtins.md) |
| 数据转换 / DataFrame | [dataframe.md](./references/dataframe.md) |
| Series 操作 | [series.md](./references/series.md) |
| 表达式 / 列运算 / 字符串 / 日期时间 | [expr.md](./references/expr.md) |
| 完整可运行示例 | [examples.md](./references/examples.md) |

### 3. API 签名的权威来源

所有函数 / 类的完整签名以 [`__builtins__.pyi`](./references/__builtins__.pyi) 为准，各 `.md` 文件仅为快速参考和示例说明。**严格按 `.pyi` 中声明的方法编写**——数据处理 API 是 Polars 风格，但只实现了 `.pyi` 中列出的子集。

### 4. 注入的全局名称，无需 `import`

`query`、`fetch`、`args`、`print`、`pl`、`DataFrame`、`Series` **都是注入到脚本作用域的全局名称，无需 `import`**。

标准库需要时可正常 `import`：`json`、`re`、`math`、`datetime`、`struct`、`hashlib` 等均可用。

### 5. `query()` 返回的时间列是字符串

`query()` 返回的 timestamp / date 列会以**字符串**形式回来，参与日期运算前需先用 `.str.to_datetime()` 或 `.str.to_date()` 转换：

```python
df = df.with_columns(pl.col("created_at").str.to_datetime())
```

### 6. 不确定时先问用户 / 先临时 return 验证，不要凭猜测

遇到以下情况，**先向用户确认或先临时 `return` 原始数据看结构**，再写处理逻辑：

- 外部 API 返回的数据结构或字段含义不明确
- 用户需求中的业务逻辑模糊（阈值、什么算"异常"等）
- 数据字段顺序 / 列名不确定
- 用户提到的表名、列名在上下文中不存在或不确定

```python
# ✅ 先临时返回，确认结构后再写处理逻辑
def main():
    res = fetch("https://api.example.com/data")
    return {"type": [str(type(res.json()))], "sample": [res.text()[:200]]}
```

## 工作流程

1. **理解用户需求** — 明确脚本目标（数据转换、清洗、生成、HTTP 调用等）
2. **获取数据** — 用 `query()` 查询数据源，或 `fetch()` 拉取外部数据
3. **先验证再处理** — 用临时 `return` 确认数据结构，**不要凭猜测写代码**
4. **数据处理** — 用 Polars 风格的 `DataFrame` / `Series` / `Expr` 做过滤、派生列、分组聚合等
5. **返回结果** — 在 `main()` 中返回处理后的数据
6. **逐步验证** — 每步操作后及时临时 `return` 中间结果检查，确认后再继续

## 核心概念

- **DataFrame** — 二维、列式的表结构，由多个等长的 `Series` 组成；`query()` 返回 DataFrame，也是 `main()` 推荐的返回类型
- **Series** — 一维、单一类型、**即时求值**的列
- **Expr** — 惰性列表达式，由 `pl.col()` / `pl.lit()` 构建，在 `select` / `with_columns` / `filter` / `group_by().agg()` 中求值；含 `.str`（字符串）和 `.dt`（日期时间）命名空间。**注意：对 Expr 做比较运算返回 Expr（惰性布尔表达式），而非 Python bool**
- **pl** — 命名空间，提供 `pl.col` / `pl.lit` 构造器、`DataFrame` / `Series` 类型，以及数据类型常量
- **DataType** — `pl.Int` / `pl.Float` / `pl.Boolean` / `pl.String` / `pl.Datetime` / `pl.Date`（精度不区分：`pl.Int32 == pl.Int64`、`pl.Float32 == pl.Float64`）

## 函数速查表

以下均为注入的全局名称，**无需 `import`**，直接使用：

| 名称 | 用途 | 详见 |
| --- | --- | --- |
| `query(sql, *args)` | SQL 取数，返回 DataFrame | [builtins.md](./references/builtins.md) |
| `fetch(url, ...)` | HTTP 请求，返回 Response | [builtins.md](./references/builtins.md) |
| `args` | 调用方传入的参数（dict） | [builtins.md](./references/builtins.md) |
| `print(...)` | 输出到脚本日志 | [builtins.md](./references/builtins.md) |
| `pl.col(name)` / `pl.lit(value)` | 构造列表达式 Expr | [expr.md](./references/expr.md) |
| `DataFrame(...)` | 二维列式表 | [dataframe.md](./references/dataframe.md) |
| `Series(...)` | 一维列 | [series.md](./references/series.md) |

## 沙箱与限制

Python 脚本在受限沙箱中执行，请注意以下边界：

- 必须定义 `main()`，否则报错
- 单次执行有**时间上限**、**内存上限**
- **无文件系统访问**——脚本不能读写本地文件
- `fetch()` 仅用于访问**外部 HTTP 服务**
- 结果超过一定行数会被**截断**

## References

本 skill 包含以下参考文档：

| 文档 | 说明 |
| --- | --- |
| [\_\_builtins\_\_.pyi](./references/__builtins__.pyi) | 全部内置类型 / 函数的类型签名（**权威来源**） |
| [builtins.md](./references/builtins.md) | `query` / `fetch` / `args` / `print` / `pl` + 数据类型 |
| [dataframe.md](./references/dataframe.md) | DataFrame + GroupBy 完整 API |
| [series.md](./references/series.md) | Series 完整 API |
| [expr.md](./references/expr.md) | Expr 惰性表达式 + `.str` / `.dt` 命名空间 |
| [examples.md](./references/examples.md) | 覆盖全部特性的可运行示例 |
