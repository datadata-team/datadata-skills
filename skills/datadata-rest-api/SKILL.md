---
name: datadata-rest-api
description: |
  本技能提供对 Datadata 平台 Rest API 的完整参考文档，在使用 Datadata Rest API 之前，**必须先加载本技能**。
  本技能提供完整的 API 端点说明和 urllib.request（零额外依赖）调用示例。
  首要用例是生成爬虫、ETL、批处理脚本，同时适用于所有需要直接调用 Datadata API 的场景。
  涵盖数据源查询、SQL 执行、结果下载、Data Spaces 表管理全流程。
  使用场景：
  1. 生成独立 Python 脚本（爬虫、ETL、批处理）
  2. 生成定时任务脚本，比如每天定时爬去最新金融数据，并写入 Data Space 数据空间。
---

## 功能概览

本 skill 提供 Datadata REST API 的完整参考文档，通过 `urllib.request`（仅标准库，零额外依赖）展示所有端点的调用方式。

**首要用例**是生成独立 Python 脚本（爬虫、ETL、批处理），但 API 文档本身是通用的 — 任何需要直接调用 Datadata API 的场景均可参考。

> **交互式操作（聊天中执行查询、探索数据等）请使用 `datadata-manual` skill。** MCP 已完整覆盖搜索、查询、Data Spaces 等日常交互功能。

### 核心能力

- **REST API 参考** — 所有端点的完整说明，含请求/响应示例
- **urllib.request 调用模板** — 即拿即用的 Python 代码片段
- **数据源操作** — 搜索、元信息、表结构、Schema 扫描
- **SQL 查询** — execute-adhoc（仅 SELECT）、结果下载（NDJSON/CSV）
- **Data Spaces** — 建表、批量写入、删除表
- **设备授权** — 脚本中自动获取/刷新 API Key

## 使用场景

| 场景              | 示例                                           |
| ----------------- | ---------------------------------------------- |
| 生成爬虫脚本      | "帮我写一个爬虫抓取数据写入 Data Space"        |
| ETL 批处理        | "写个脚本每天从 MySQL 导出数据到 CSV"          |
| 自动化数据流水线  | "生成脚本定时查询 Datadata 并发送报告"         |
| 查阅 API 文档     | "Datadata 的 execute-adhoc 接口怎么调？"       |
| Datadata API 集成 | "给我一个 Python 示例调用 Datadata API 查数据" |

> 以下场景请使用 **`datadata-manual`** skill：
>
> - 聊天中交互式查询数据（"帮我查一下销售数据"）
> - 探索数据源结构（"看看这个 datasource 有哪些表"）
> - 设置表/列注释、触发扫描等即时操作

## 概念

- **Datasource** — 查询目标的数据源。不同类型的 datasource（ducklake、MySQL、ClickHouse、CSV 等）有不同的表命名约定。
- **Data space** — 录入数据的目标。`ducklake` 类型 datasource 独有的能力，支持创建表、批量插入和删除表。data-space 名称为 datasource 的 `name`（通过 `/datasources/{id}/info` 获取）。
- **Query** (`execute-adhoc`) — **只读**抽象，包含 SQL 脚本（仅 SELECT）、datasource 绑定和查询引擎类型。
- **Execution** — 查询的后台执行实例。通过 `/executions/{id}/result` 异步获取结果。

## API Key

### 手动设置（推荐用于脚本）

```bash
export DATADATA_API_KEY="ak_..."
export DATADATA_BASE_URL="https://www.datadata.com"  # 可选，本地开发时覆盖
```

API Key 在 Datadata 网页端创建：登录 → 头像 → Settings → API Keys → 创建新 Key。

所需权限：

- `datasources:read` — 查询元信息
- `queries:execute-adhoc` — 执行 SQL
- `executions:get` — 获取查询结果
- `datasources:scan` — 设置注释、触发扫描
- `data-spaces:write` — Data Spaces 表管理（爬虫写入场景必需）

### 设备授权（适用于无人值守脚本）

脚本中可通过设备授权自动获取 API Key（有效期 90 天）：

```python
# Step 1: 发起设备授权
resp = _request(f"{BASE_URL}/api/v1/api-keys/device-flow/code", method="POST")
print(f"请打开: {resp['verificationUriComplete']}")

# Step 2: 等待用户完成登录后换取 token
resp2 = _request(f"{BASE_URL}/api/v1/api-keys/device-flow/token", method="POST",
                 payload={"deviceCode": resp["deviceCode"]})
api_key = resp2["apiKey"]["key"]
```

## Python 请求模板

所有脚本的基础模板（仅标准库，零依赖）：

```python
import json, urllib.request, os

API_KEY = os.environ.get("DATADATA_API_KEY", "ak_...")
BASE_URL = os.environ.get("DATADATA_BASE_URL", "https://www.datadata.com")

def _request(url, method="GET", payload=None):
    headers = {"X-Datadata-Api-key": API_KEY, "Accept": "application/json"}
    data = json.dumps(payload).encode() if payload else None
    if payload:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw else None
```

## 规则

### 🔴 搜索数据源：必须让用户确认，禁止自动选用

搜索结果**绝不能**由 Agent 自动选取。将结果以序号列表呈现，等待用户明确选择。

### 🔴 最小操作原则：完成一步即停

Agent 只执行用户**明确要求**的操作。生成脚本后立即停止，不要自动运行或推断后续步骤。

### 🔴 生成的脚本必须零依赖

只使用 Python 标准库（`urllib.request`、`json`、`os` 等），不依赖 `requests`、`pandas` 等第三方库。

### 查询只读

`execute-adhoc` **仅支持 SELECT**。INSERT/UPDATE/DELETE/DDL 请使用 Data Spaces 的 `insert-rows` 端点。

### 结果处理

生成的脚本应将查询结果保存到文件，不要硬编码打印大数据集。

## References

| 文档                                                       | 说明                               |
| ---------------------------------------------------------- | ---------------------------------- |
| [./references/api.md](./references/api.md)                 | REST API 端点完整参考              |
| [./references/query-guide.md](./references/query-guide.md) | 查询引擎、表命名、标识符引用       |
| [./references/data-spaces.md](./references/data-spaces.md) | Data Spaces 表管理（爬虫写入必备） |

### 相关 skill

- **`datadata-dql`** — DQL（Starlark）数据处理脚本编写
