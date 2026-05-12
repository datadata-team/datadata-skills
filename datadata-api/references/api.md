# Datadata API Reference

Base URL: `https://www.datadata.com/api/v1` (override via `DATADATA_BASE_URL` for local dev)

Authentication: `X-Datadata-Api-key` header with an API key.

---

## Direct API vs CLI

The skill provides two ways to use these APIs:

- **CLI** (`datadata_query.py`) — best for interactive exploration and one-off queries. All endpoints below have a CLI subcommand.
- **Direct API calls** — preferred for generated scripts (crawlers, ETL pipelines, batch jobs). Use `urllib.request` (stdlib, zero dependencies) to call the API directly — it avoids the subprocess overhead and gives full control over error handling.

Python helper template:

```python
import json, urllib.request

API_KEY = "..."
BASE_URL = "https://www.datadata.com/api/v1"

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

---

## Endpoint summary

| Group       | Method | Path                               | Auth permission         | CLI subcommand         |
| ----------- | ------ | ---------------------------------- | ----------------------- | ---------------------- |
| Datasource  | GET    | `/datasources/{id}/info`           | `datasources:read`      | `get-datasource-info`  |
| Datasource  | GET    | `/datasources/{id}/list-tables`    | `datasources:read`      | `list-tables`          |
| Datasource  | GET    | `/datasources/{id}/describe-table` | `datasources:read`      | `describe-table`       |
| Datasource  | POST   | `/datasources/{id}/scan`           | `datasource:scan`       | `scan-datasource`      |
| Execution   | POST   | `/queries/execute-adhoc`           | `queries:execute-adhoc` | `execute-adhoc`        |
| Execution   | GET    | `/executions/{id}/result`          | `executions:get`        | `get-execution-result` |
| Data Spaces | POST   | `/data-spaces/{id}/create-table`   | `data-spaces:write`     | `create-table`         |
| Data Spaces | POST   | `/data-spaces/{id}/describe-table` | `data-spaces:write`     | — (direct only)        |
| Data Spaces | POST   | `/data-spaces/{id}/drop-table`     | `data-spaces:write`     | — (direct only)        |
| Data Spaces | POST   | `/data-spaces/{id}/insert-rows`    | `data-spaces:write`     | `insert-rows`          |

---

## Datasource APIs

### Get datasource info

`GET /datasources/{datasourceId}/info`

Returns metadata such as datasource type, engine, and display name. Always check the `type` field — only `ducklake` datasources support data-spaces operations.

CLI:

```bash
python3 scripts/datadata_query.py get-datasource-info --datasource-id "CXNGJifvqE48kdzKVC9o5"
```

Direct:

```python
data = _request(f"{BASE_URL}/datasources/CXNGJifvqE48kdzKVC9o5/info")
print(data["type"])  # e.g. "ducklake"
```

### List tables

`GET /datasources/{datasourceId}/list-tables?schemaName={schema}`

`schemaName` is optional — omit to list all schemas.

CLI:

```bash
python3 scripts/datadata_query.py list-tables --datasource-id "CXNGJifvqE48kdzKVC9o5" --schema-name "main"
```

Direct:

```python
data = _request(f"{BASE_URL}/datasources/CXNGJifvqE48kdzKVC9o5/list-tables?schemaName=main")
```

### Describe table

`GET /datasources/{datasourceId}/describe-table?schemaName={schema}&tableName={table}`

> This is the **datasource** describe-table endpoint. For the data-spaces variant, see [below](#describe-table-data-spaces).

CLI:

```bash
python3 scripts/datadata_query.py describe-table \
  --datasource-id "CXNGJifvqE48kdzKVC9o5" \
  --schema-name "main" \
  --table-name "customers"
```

Direct:

```python
data = _request(f"{BASE_URL}/datasources/CXNGJifvqE48kdzKVC9o5/describe-table?schemaName=main&tableName=customers")
```

**Response:**

```json
{
  "columns": [
    {
      "column_name": "id",
      "data_type": "INTEGER",
      "is_nullable": "NO",
      "column_default": null
    }
  ]
}
```

### Scan datasource schema

`POST /datasources/{datasourceId}/scan`

Triggers an asynchronous table structure scan for the datasource. Returns immediately with a task ID — the scan runs in the background. Designed for non-ducklake datasources that need background schema discovery.

For **data-spaces (ducklake)**, use the data-spaces `describe-table` endpoint instead for real-time results.

CLI:

```bash
python3 scripts/datadata_query.py scan-datasource --datasource-id "CXNGJifvqE48kdzKVC9o5"
```

Direct:

```python
data = _request(f"{BASE_URL}/datasources/CXNGJifvqE48kdzKVC9o5/scan", method="POST")
print(data["taskId"])  # Asynq task ID
```

**Response:**

```json
{
  "taskId": "string",
  "taskType": "scan",
  "state": "active"
}
```

| Status | Description          |
| ------ | -------------------- |
| 200    | Scan task created    |
| 404    | Datasource not found |

---

## Execution APIs

### Create execution (execute adhoc query)

`POST /queries/execute-adhoc`

Body:

| Field         | Type              | Required | Default  | Description                                          |
| ------------- | ----------------- | -------- | -------- | ---------------------------------------------------- |
| `script`      | string            | Yes      | —        | SQL or script content                                |
| `scriptType`  | string            | No       | `sql`    | Script type                                          |
| `queryEngine` | string            | No       | `duckdb` | `duckdb` or `clickhouse`                             |
| `datasources` | array of bindings | No       | `[]`     | `[{datasourceId, attachAlias}]` — cross-source joins |

CLI:

```bash
python3 scripts/datadata_query.py execute-adhoc \
  --script-type sql \
  --query-engine duckdb \
  --datasource "CXNGJifvqE48kdzKVC9o5:orders" \
  --script "SELECT * FROM orders.public.customers LIMIT 10"
```

Direct:

```python
payload = {
    "script": "SELECT * FROM orders.public.customers LIMIT 10",
    "scriptType": "sql",
    "queryEngine": "duckdb",
    "datasources": [{"datasourceId": "CXNGJifvqE48kdzKVC9o5", "attachAlias": "orders"}],
}
response = _request(f"{BASE_URL}/queries/execute-adhoc", method="POST", payload=payload)
execution_id = response.get("id") or response.get("executionId")
```

**Response** contains an execution `id` — the query runs asynchronously. Use `find_execution_id()` (recursive search) to extract it from the nested response.

### Get execution result

`GET /executions/{executionId}/result?format={fmt}&timeout={sec}`

| Query param | Required | Default  | Description                                |
| ----------- | -------- | -------- | ------------------------------------------ |
| `format`    | No       | `ndjson` | `ndjson` or `csv`                          |
| `timeout`   | No       | —        | Seconds for backend to wait for completion |

CLI:

```bash
python3 scripts/datadata_query.py get-execution-result \
  --execution-id "CaU6DR..." \
  --format ndjson \
  --timeout 30
```

Direct:

```python
url = f"{BASE_URL}/executions/CaU6DR.../result?format=ndjson&timeout=30"
req = urllib.request.Request(url, headers={"X-Datadata-Api-key": API_KEY})
with urllib.request.urlopen(req) as resp:
    raw = resp.read().decode()
    rows = [json.loads(line) for line in raw.strip().splitlines() if line.strip()]
    print(f"Got {len(rows)} rows")
```

For CSV format, the response is plain text:

```python
url = f"{BASE_URL}/executions/CaU6DR.../result?format=csv"
```

If the query is still running after `timeout`, the API returns a timeout error. Use a longer timeout or save the `executionId` and check later.

---

## Data Spaces APIs

> **Note:** Only datasources of type `ducklake` support data-spaces operations. Check with `get-datasource-info` first.

### Create table

`POST /data-spaces/{datasourceId}/create-table`

Body:

| Field       | Type   | Required | Description                                    |
| ----------- | ------ | -------- | ---------------------------------------------- |
| `tableName` | string | Yes      | Table name                                     |
| `columns`   | array  | Yes      | `[{"columnName": "...", "columnType": "..."}]` |

Valid `columnType` values: `INTEGER`, `VARCHAR`, `DOUBLE`, `BOOLEAN`, `TIMESTAMP`, `BIGINT`, `FLOAT`, etc.

CLI:

```bash
python3 scripts/datadata_query.py create-table \
  --datasource-id "123" \
  --table-name "products" \
  --columns '[{"columnName": "id", "columnType": "INTEGER"}, {"columnName": "name", "columnType": "VARCHAR"}]'
```

Direct:

```python
payload = {
    "tableName": "products",
    "columns": [
        {"columnName": "id", "columnType": "INTEGER"},
        {"columnName": "name", "columnType": "VARCHAR"},
    ],
}
_request(f"{BASE_URL}/data-spaces/123/create-table", method="POST", payload=payload)
```

| Status | Description          |
| ------ | -------------------- |
| 204    | Created              |
| 404    | Data space not found |
| 409    | Table already exists |

### Describe table (data spaces)

`POST /data-spaces/{datasourceId}/describe-table`

Body:

| Field       | Type   | Required | Description |
| ----------- | ------ | -------- | ----------- |
| `tableName` | string | Yes      | Table name  |

No CLI subcommand — call directly:

```python
payload = {"tableName": "products"}
data = _request(f"{BASE_URL}/data-spaces/123/describe-table", method="POST", payload=payload)
for col in data["columns"]:
    print(col["column_name"], col["data_type"])
```

### Drop table

`POST /data-spaces/{datasourceId}/drop-table`

Body:

| Field       | Type   | Required | Description |
| ----------- | ------ | -------- | ----------- |
| `tableName` | string | Yes      | Table name  |

No CLI subcommand — call directly:

```python
payload = {"tableName": "products"}
_request(f"{BASE_URL}/data-spaces/123/drop-table", method="POST", payload=payload)
```

| Status | Description          |
| ------ | -------------------- |
| 200    | Dropped              |
| 404    | Data space not found |

### Insert rows

`POST /data-spaces/{datasourceId}/insert-rows`

Body:

| Field       | Type          | Required | Description                            |
| ----------- | ------------- | -------- | -------------------------------------- |
| `tableName` | string        | Yes      | Table name                             |
| `columns`   | array[string] | Yes      | Column names matching the target table |
| `rows`      | array[array]  | Yes      | Row data, ordered by `columns`         |

Insert is transactional — all rows succeed or none are written. `map[string]any` values are auto-serialized to JSON strings.

CLI:

```bash
python3 scripts/datadata_query.py insert-rows \
  --datasource-id "123" \
  --table-name "products" \
  --columns '["id", "name", "price"]' \
  --rows '[[1, "Widget", 9.99], [2, "Gadget", 24.99]]'
```

Direct:

```python
payload = {
    "tableName": "products",
    "columns": ["id", "name", "price"],
    "rows": [
        [1, "Widget", 9.99],
        [2, "Gadget", 24.99],
    ],
}
_request(f"{BASE_URL}/data-spaces/123/insert-rows", method="POST", payload=payload)
```

| Status | Description          |
| ------ | -------------------- |
| 200    | Inserted             |
| 400    | Table not found      |
| 404    | Data space not found |

---

## Common errors

| Status | Meaning                                                                             |
| ------ | ----------------------------------------------------------------------------------- |
| 401    | Unauthenticated — API key missing or invalid                                        |
| 403    | Forbidden — API key lacks required permission                                       |
| 404    | Endpoint does not exist at this base URL (do NOT retry — check `DATADATA_BASE_URL`) |
| 5xx    | Server error — retry once after 3s, then report the `executionId` if applicable     |
