---
name: datadata-dql
description: |
  本技能包含了 Datadata DQL 查询脚本语言的完整参考文档，当使用 Datadata DQL 脚本时，**必须先加载本技能**。
  Write DQL data processing scripts for the Datadata platform — a Starlark-based extended scripting language supporting DataFrame/Series operations,
  SQL queries, HTTP requests, and more. Use when the user needs to write data transformation, data cleaning, data generation, or custom data processing logic.
---

# Datadata Query Language (DQL) 脚本编写

DQL 是基于 Starlark 的自定义脚本语言，扩展了 Starlark 的语法和标准库，提供数据处理、HTTP 网络调用等能力。

## 🔴 核心规则

### 1. 脚本必须有 `return` 语句

DQL 脚本实际是一个函数的 body，**最后必须有 `return` 语句**返回数据，否则执行结果为空。

```python
# ✅ 正确
df = query("SELECT * FROM users")
return df

# ❌ 错误：没有 return，结果为空
df = query("SELECT * FROM users")
```

### 2. 编写前必须先阅读 grammar.txt（语法规范）

DQL 基于 Starlark。**编写任何 DQL 脚本前，必须先阅读 [grammar.txt](./references/grammar.txt)**（Starlark EBNF 语法），严格按其允许的语法结构编写，**不得套用 grammar.txt 未定义的语法**。

### 3. 必须先阅读对应的 References 文档

**禁止仅凭本文档就编写 DQL 代码。** 本文档只是索引，实际 API 签名、参数、返回值以 references 为准。

> **两类"必读"分工**：[grammar.txt](./references/grammar.txt) 管**语法**（所有脚本都要先读，见上一条）；各 `.md` 管 **API**（按场景读）。

编写代码前至少阅读以下对应文档：

| 场景                   | 必读文档                                                                                          |
| ---------------------- | ------------------------------------------------------------------------------------------------- |
| SQL 查询               | [query.md](./references/query.md)                                                                 |
| HTTP 请求              | [fetch.md](./references/fetch.md)                                                                 |
| 数据转换 / DataFrame   | [dataframe.md](./references/dataframe.md)                                                         |
| Series 操作            | [series.md](./references/series.md)                                                               |
| 时间处理 / 数学 / JSON | [time.md](./references/time.md)、[math.md](./references/math.md)、[json.md](./references/json.md) |
| concat / throw / print | [builtins.md](./references/builtins.md)                                                           |
| 2D 绘图                | [canvas_drawing.md](./references/canvas_drawing.md)                                               |

### 4. 关于 API 文档的权威来源

所有函数/类的完整签名定义以 [**builtins**.pyi](./references/builtins.pyi) 为准，各 `.md` 文件仅为快速参考和示例说明。

### 5. 所有 DQL 扩展均为内置全局名称

`query`、`fetch`、`concat`、`throw`、`json`、`math`、`time`、`canvas`、`DataFrame`、`Series` **都是内置的全局名称，无需 `import`**。

### 6. 不确定时先问用户，不要自行猜测

当遇到以下情况时，**必须**先向用户确认，而不是自行假设：

- 外部 API 返回的数据结构或字段含义不明确
- 用户需求中的业务逻辑模糊（如：什么是"异常"、阈值是多少）
- 数据字段顺序不确定（如 K 线的 `[开, 高, 低, 收]` 还是 `[开, 收, 低, 高]`）
- 用户提到的表名、列名在上下文中不存在或不确定

```python
# ❌ 错误：自行猜测字段顺序，导致结果错误
data = resp.body["klines"]
df = DataFrame(data, columns=["time", "open", "high", "low", "close"])  # 猜错了

# ✅ 正确：先输出类型和数据给用户确认
return {"type": type(resp.body), "data": resp.body}  # 让用户确认类型和数据结构
# 然后根据用户反馈再写处理逻辑
```

## 工作流程

0. **阅读语法规范** — 编写前先读 [grammar.txt](./references/grammar.txt)，确认可用语法（见核心规则第 2 条）
1. **理解用户需求** — 确定脚本的目标（数据转换、数据清洗、数据生成、可视化、HTTP 调用等）
2. **查询数据** — 使用 `query()` 或 `fetch()` 获取数据
3. **先验证数据再处理** — 用 `return` 临时返回原始数据确认结构，**不要凭猜测写代码**
4. **数据处理** — 使用 Series/DataFrame 的方法进行数据操作（过滤、转换、聚合等）
5. **生成结果** — 返回处理后的数据或结果对象
6. **逐步验证** — 每步操作后及时 `return` 临时返回中间结果来检查，确认后再继续

## 核心概念

- **DataFrame**：二维表格，可访问列 (`df['col']`)、行 (`df[0]`)，支持分组、排序、合并等操作
- **Series**：一维列数据，支持映射 (`.map()`)、过滤、统计聚合等
- **Timestamp**：时间戳类型，用于时间序列的滚动窗口和重采样（详见 [time.md](./references/time.md)）
- **DType**：数据类型包括 `int`, `float`, `string`, `date`, `timestamp` 等

## 模块和函数速查

以下均为内置全局名称，**无需 `import`**，直接使用：

| 名称                  | 用途      | 详见                                                |
| --------------------- | --------- | --------------------------------------------------- |
| `query(sql, ...)`     | SQL 查询  | [query.md](./references/query.md)                   |
| `fetch(url, ...)`     | HTTP 请求 | [fetch.md](./references/fetch.md)                   |
| `DataFrame()`         | 二维表格  | [dataframe.md](./references/dataframe.md)           |
| `Series()`            | 一维列    | [series.md](./references/series.md)                 |
| `math.ceil(x)` 等     | 数学函数  | [math.md](./references/math.md)                     |
| `time.time()` 等      | 时间处理  | [time.md](./references/time.md)                     |
| `json.dumps(x)` 等    | JSON 处理 | [json.md](./references/json.md)                     |
| `concat([df1, df2])`  | 连接数据  | [builtins.md](./references/builtins.md)             |
| `throw(err)`          | 抛出错误  | [builtins.md](./references/builtins.md)             |
| `print(...)` 等       | 内置函数  | [builtins.md](./references/builtins.md)             |
| `canvas.Context(w,h)` | 2D 绘图   | [canvas_drawing.md](./references/canvas_drawing.md) |

## 使用场景

各模块参考文档中均包含实用示例：

- **数据清洗、聚合、合并、异常检测、RFM 分析** → [dataframe.md](./references/dataframe.md)
- **月度对比、每日活跃用户** → [query.md](./references/query.md)
- **外部 API 集成、发送数据到外部服务** → [fetch.md](./references/fetch.md)
- **时间处理与时间戳** → [time.md](./references/time.md)
- **JSON 序列化与格式化** → [json.md](./references/json.md)
- **数学计算** → [math.md](./references/math.md)
- **错误处理与数据验证** → [builtins.md](./references/builtins.md)
- **Canvas 基础图形绘制** → [canvas_drawing.md](./references/canvas_drawing.md)
- **调试技巧、性能优化、常见陷阱** → [faq_best_practices.md](./references/faq_best_practices.md)（脚本出错或性能不佳时查阅）

## 输出规则

- **脚本最后必须有 `return` 语句**，DQL 脚本是函数的 body，无 `return` 则结果为空
- 可返回 DataFrame、dict、list 或其他可序列化的数据结构
- 返回值会自动转换为 JSON 并发送给前端
- 避免返回过大的数据结构（> 1MB），必要时加入 LIMIT 限制

## Starlark 基础

DQL 基于 Starlark，支持：

```
# 基本类型
x = 42                      # 整数
s = "hello"                 # 字符串
lst = [1, 2, 3]            # 列表
d = {"key": "value"}        # 字典

# 控制流
if x > 0:
    print("positive")
for i in range(5):
    print(i)

# 函数和 Lambda
def add(a, b):
    return a + b
square = lambda x: x * x
```

详见 [Starlark 官方文档](https://github.com/bazelbuild/starlark/blob/master/spec.md)。

## References

本 skill 包含以下参考文档：

| 文档                                                | 说明                                    |
| --------------------------------------------------- | --------------------------------------- |
| [grammar.txt](./references/grammar.txt)             | Starlark EBNF 语法规范（编写前必读）    |
| [dataframe.md](./references/dataframe.md)           | DataFrame 完整 API 参考                 |
| [series.md](./references/series.md)                 | Series 完整 API 参考                    |
| [query.md](./references/query.md)                   | SQL 查询（query）参考                   |
| [fetch.md](./references/fetch.md)                   | HTTP 请求（fetch）参考                  |
| [math.md](./references/math.md)                     | 数学函数（math）参考                    |
| [time.md](./references/time.md)                     | 时间处理（time）参考                    |
| [json.md](./references/json.md)                     | JSON 处理（json）参考                   |
| [builtins.md](./references/builtins.md)             | 内置函数（concat, throw, print 等）参考 |
| [canvas_drawing.md](./references/canvas_drawing.md) | Canvas 2D 绘图 API + 示例               |

### 外部资源

- **语法规范**：[grammar.txt](./references/grammar.txt) — Starlark EBNF 语法（编写前必读，权威来源）
- **Starlark 官方文档**：[Starlark 官方文档](https://github.com/bazelbuild/starlark/blob/master/spec.md)
- **完整 API 签名**：[**builtins**.pyi](./references/builtins.pyi) — 所有类型提示（权威来源）
- **Starlark 语言**：https://github.com/bazelbuild/starlark/blob/master/spec.md — 官方 Starlark 语言规范
