# 设计：新增 datadata-python skill（Python 查询脚本编写）

- 日期：2026-07-27
- 新增 skill：`datadata-python`
- 参照模板：`datadata-dql`

## 1. 背景与动机

Datadata 后端新增了**第三种查询脚本类型 `python`**（与 `sql`、`dql` 并列，见 `internal/models/query.go` 的 `QueryScriptType`，由 `internal/infra/query_executor/executor.go` 统一分发到 `python_executor`）。它运行**真正的 Python**（RustPython 编译为 WebAssembly，在沙箱中执行），数据处理 API 采用 **Polars 风格**的 `DataFrame` / `Series` / `Expr`。

现有 `datadata-dql` skill 教 AI 编写 DQL 脚本；现需**对称地**新增 `datadata-python` skill，教 AI 编写平台的 Python 查询脚本。

**核心问题**：若缺少准确参考，AI 会把它当成完整的 Python / 真 Polars / pandas，调用大量执行器**未实现**的方法，导致脚本跑不通。
**解决思路**：提供一份「我们有什么」的**完整、准确的正面参考**（签名以执行器的 `builtins.pyi` 为权威源），并配一套**全部经真实执行验证**的示例。**不使用「不支持的 API」黑名单**——用准确的正面描述收敛，而非负面清单。

## 2. 目标与非目标

**目标**

- 新建 `skills/datadata-python/`，定位为**纯语言/API 参考**，结构与 `datadata-dql` 对称。
- references 采用**细粒度拆分**；以 `builtins.pyi` 为签名权威源。
- 新增 `examples.md`，覆盖**全部现有特性**，且每个示例**先经真实执行验证**再写入。
- 把 `datadata-python` 注册为仓库第 5 个 skill，同步更新仓库元数据。

**非目标**

- 不覆盖「如何运行 Python 脚本」（执行方式交给 `datadata-manual` / `datadata-rest-api`，本 skill 仅用一句话指向）。
- 不修改后端代码，不改动 MCP 工具 enum（当前 MCP `execute-adhoc`/`patch-query` 仍只 advertise `sql,dql`——属后端范畴，本 skill 不处理）。
- 不写「不支持 / 禁止臆造」的负面清单。
- 不含 canvas 绘图、`math`/`time`/`json` 全局模块（这些在 DQL 里有，Python 里 `math`/`datetime`/`json` 是标准库 `import`，无 canvas 能力）。

## 3. Skill 结构

```
skills/datadata-python/
├── SKILL.md                    核心规则 + 工作流 + 核心概念 + 速查表 + References 索引
└── references/
    ├── builtins.pyi        逐字复制自后端 lib/python-executor/builtins.pyi（签名权威源）
    ├── builtins.md             query / fetch / args / print / pl 命名空间 + DataType 数据类型
    ├── dataframe.md            DataFrame + GroupBy 完整 API
    ├── series.md               Series 完整 API
    ├── expr.md                 Expr 惰性表达式 + .str / .dt 命名空间
    └── examples.md             全部特性的可运行示例（每条经执行验证）
```

## 4. 与 datadata-dql 的关键差异（决定内容，而非照抄）

| 维度           | datadata-dql                                                       | datadata-python                                                                               |
| -------------- | ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| 语言           | Starlark（需 `grammar.txt` EBNF 语法）                             | 真 Python，**不需要 grammar.txt**（语法为通用知识）                                           |
| 入口           | 脚本体末尾 `return`                                                | **必须定义 `main()`**，返回值即结果                                                           |
| DataFrame 风格 | pandas 风格（`.map` / `.loc` / `rolling` / `pivot`）               | **Polars 风格**（`pl.col` / `select` / `with_columns` / `group_by().agg()` / 惰性 `Expr`）    |
| 注入全局名     | `query` `fetch` `json` `math` `time` `canvas` `DataFrame` `Series` | `query` `fetch` `args` `print` `pl` `DataFrame` `Series`（无 canvas，无 math/time/json 全局） |
| 参数           | —                                                                  | `args`（始终是 dict）全局注入                                                                 |
| 标准库         | Starlark 内置                                                      | 冻结的 Python 标准库可 `import`（`json`/`re`/`math`/`datetime`/`struct`/`hashlib` 等）        |

## 5. SKILL.md 大纲

- **frontmatter `description`**：中英双语（中文触发说明 + 英文半句供 skill 路由）。要点：写 Datadata Python 查询脚本时必须先加载；数据转换/清洗/生成、Polars 风格 DataFrame、SQL 取数、HTTP 请求。
- **核心规则（正向表述）**
  1. 脚本**必须定义 `main()`**，返回值即结果（`DataFrame` / `Series` / `list[dict]` / 其它 JSON 可序列化值）。
  2. 编写前**必读对应 reference**；API 签名以 `references/builtins.pyi` 为**权威源**，严格按其声明编写。
  3. `query` / `fetch` / `args` / `print` / `pl` / `DataFrame` / `Series` 是注入的全局名，无需 `import`；标准库可 `import`。
  4. `query()` 返回的**时间列是字符串**，需 `.str.to_datetime()` / `.str.to_date()` 转换。
  5. 不确定数据结构时，先临时 `return` 验证再写处理逻辑，不要凭猜测（沿用 dql 精神）。
- **工作流**：理解需求 → `query()`/`fetch()` 取数 → 临时 return 验证结构 → Polars 风格处理 → `main()` 返回结果 → 逐步验证。
- **核心概念**：`DataFrame`（二维列式表）、`Series`（即时求值单列）、`Expr`（惰性列表达式，含 `.str`/`.dt`）、`pl`（构造器 + dtype）、`DataType`（Int/Float/Boolean/String/Datetime/Date；精度不区分）。
- **模块与函数速查表**：`query` / `fetch` / `args` / `print` / `pl.col` / `pl.lit` / `DataFrame` / `Series` → 各自 reference。
- **References 索引表**：列出全部 references 文件及用途。

## 6. references 内容映射（数据来源）

一手来源：后端 `lib/python-executor/builtins.pyi`（Polars 风格 DataFrame/Series/Expr 的手写类型 stub，标注 source of truth）与 `src/fetch_prelude.py`（fetch/Response/Headers）。可参照已写好的 `datadata-docs/docs/guides/python/` 参考页改写为 **AI 面向**（更强调「必读 / 按 .pyi 声明」）。

- `builtins.pyi` — 逐字复制后端同名文件。
- `builtins.md` — `query(sql, *args)`、`fetch(url, method, body, headers, timeout)` + `Response`（`ok`/`status`/`status_text`/`headers.get`/`text()`/`json()`）、`args`、`print`、`pl`（`col`/`lit`/`DataFrame`/`Series`/dtype 常量）、DataType 说明。
- `dataframe.md` — 构造、属性（`columns`/`dtypes`/`schema`/`shape`/`height`/`width`）、`is_empty`/`select`/`with_columns`/`filter`/`group_by`、导出（`to_dicts`/`rows`/`to_dict`/`get_column`/`__getitem__`），以及 `GroupBy.agg`。
- `series.md` — 构造、`name`/`dtype`、转换清洗（`to_list`/`cast`/`abs`/`round`/`fill_null`/`is_null`/`is_not_null`/`filter`/`alias`/`rename`）、聚合、索引、运算符重载。
- `expr.md` — `pl.col`/`pl.lit` 构建；通用方法、聚合方法、运算符（**比较返回 Expr 而非 bool**）、`.str`（contains/starts_with/…/to_datetime/to_date）、`.dt`（year/…/truncate/strftime）。

## 7. examples.md 与执行验证方法论（硬性要求）

**每个示例在写入前，必须用真实执行器跑通。**

**验证路径（最省事、最faithful，无需构建/外部服务）**：后端 `internal/infra/python_executor/python_executor.wasm` 已提交并 `go:embed`，`init()` 在进程内编译运行，纯脚本执行**无需 Redis/DB/网络**。

- 在 `internal/infra/python_executor/` 包内新建**临时** `examples_verify_test.go`，用表驱动逐条调用：
  - `Execute(ctx, &models.Execution{Script: ...})`（`executor.go`，返回 `result.Dataset` / `result.ScriptLogs`，Python 错误折叠进返回 `error`）；或
  - 低层 `pyRuntime.execute(ctx, ExecuteInput{Script, Params})`（`plugin.go`，返回 `out.Dataset` / `out.Logs` / `out.Error`）。
- 运行：`go test ./internal/infra/python_executor/ -run TestVerifyExamples -v -timeout 60s`（始终带 `-timeout`）。
- `query()` 示例：按 `query_e2e_test.go` 用 `httptest.Server` mock queryserver + `setupTestConfig(t, url)` 返回固定 dataset（不连真实数据源）。
- `fetch()` 示例：按 `fetch_e2e_test.go` 用 `httptest.NewServer` + `allowLoopbackForTest(t)`（私网仍被拦截）。
- **验证通过后删除临时测试文件**，不在 `datadata-pegasus` 仓库留下任何改动。

**examples.md 特性覆盖清单（逐条验证）**

1. `main()` 返回 `list[dict]`
2. `main()` 返回 `DataFrame`（构造）
3. `main()` 返回 `Series`（构造）
4. `main()` 返回 `dict` / 其它 JSON 值
5. `args` 读取参数（配 `Params` 传入）
6. `query()` 取数（mock）
7. `query()` 时间列 `.str.to_datetime()` 转换
8. `fetch()` GET + `res.ok`/`res.json()`（mock）
9. `fetch()` POST + `body` 自动 JSON 序列化（mock）
10. DataFrame `select` / `with_columns` / `filter`
11. DataFrame `group_by().agg()`
12. DataFrame 导出（`to_dicts` 等）
13. Series 构造 / 聚合 / `filter` / 运算符
14. Expr `.str`（如 `to_uppercase`/`contains`/`to_datetime`）
15. Expr `.dt`（如 `year`/`truncate`）
16. Expr 聚合 + `alias`；`pl.col`/`pl.lit`；`cast`
17. `print(...)` → 日志（校验 `ScriptLogs`/`out.Logs`）
18. 标准库 `import`（`json`/`re`/`math`/`datetime`/`hashlib` 各验一次）

## 8. 内容口径与约束

- 正文中文；`description` 带英文半句（供 skill 路由，与其它 skill 一致）。
- Markdown **不换行**（仓库 `.editorconfig` / `.vscode` 约定）。
- 沙箱相关表述与已审阅过的 `datadata-docs` 口径一致：可写「无文件系统访问、`fetch` 仅访问外部服务、结果超限截断、执行超时/内存上限」等边界，但**不暴露** SSRF 防御机制细节、`random` 不可用等实现内幕。
- 所有函数/类签名一律以 `builtins.pyi` 为准，`.md` 仅作快速参考与示例。

## 9. 仓库元数据同步（注册为第 5 个 skill）

- `AGENTS.md` — skill 表新增一行；File structure 树补 `skills/datadata-python/`；Developer commands 补两条 `npx skills add ./skills/datadata-python --agent {claude-code,codex} --global`；Editing guidance 补一条（`.pyi` 与 `.md` 保持同步）。
- `CLAUDE.md` — 「The four skills」→ 五个，新增 `datadata-python` 段落说明。
- `README.md` / `README_zh.md` — skill 列表与安装命令补 `datadata-python`。

## 10. 提交方式

`datadata-skills` 为独立 git 仓库。按用户习惯（**从不留正式 commit**），spec 与 skill 文件写入工作区，**不执行 commit**，由用户自行提交。验证用的临时 Go 测试文件在验证后删除。

## 11. 验收标准

- `skills/datadata-python/` 结构完整，可 `npx skills add` 安装。
- `examples.md` 全部示例经真实执行器验证通过；验证用临时测试文件已删除，`datadata-pegasus` 无残留改动。
- `references/builtins.pyi` 与后端同名文件一致；各 `.md` 与 `.pyi` 声明一致。
- 仓库元数据（AGENTS/CLAUDE/README/README_zh）均含第 5 个 skill。
- 无「不支持的 API」负面清单；内容为正面描述。
