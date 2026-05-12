# Data Spaces API

Base path: `/api/v1/data-spaces`

Authentication: API Key with `data-spaces:write` permission required on all endpoints.

---

## Create Table

`POST /api/v1/data-spaces/{datasourceId}/create-table`

在指定的数据空间中创建一张新表。

### Path Parameters

| Name         | Type    | Description |
| ------------ | ------- | ----------- |
| datasourceId | integer | 数据源 ID   |

### Request Body

```json
{
  "tableName": "string",
  "columns": [
    {
      "columnName": "string",
      "columnType": "string"
    }
  ]
}
```

| Field                | Type   | Validation      | Description                                    |
| -------------------- | ------ | --------------- | ---------------------------------------------- |
| tableName            | string | required        | 表名                                           |
| columns              | array  | required, min=1 | 列定义列表                                     |
| columns[].columnName | string | required        | 列名                                           |
| columns[].columnType | string | required        | 列类型（如 `INTEGER`, `VARCHAR`, `DOUBLE` 等） |

### Responses

| Status         | Description    |
| -------------- | -------------- |
| 204 No Content | 创建成功       |
| 404 Not Found  | 数据空间不存在 |
| 409 Conflict   | 表已存在       |

---

## Describe Table

`POST /api/v1/data-spaces/{datasourceId}/describe-table`

查询数据空间中指定表的列信息。

### Path Parameters

| Name         | Type    | Description |
| ------------ | ------- | ----------- |
| datasourceId | integer | 数据源 ID   |

### Request Body

```json
{
  "tableName": "string"
}
```

| Field     | Type   | Validation | Description |
| --------- | ------ | ---------- | ----------- |
| tableName | string | required   | 表名        |

### Responses

| Status | Description          |
| ------ | -------------------- |
| 200 OK | 成功，返回列信息列表 |

Response body:

```json
{
  "columns": [
    {
      "table_catalog": "ducklake",
      "table_schema": "string",
      "table_name": "string",
      "column_name": "string",
      "ordinal_position": 1,
      "COLUMN_COMMENT": null,
      "data_type": "string",
      "is_nullable": "YES",
      "column_default": null
    }
  ]
}
```

| Status        | Description    |
| ------------- | -------------- |
| 200 OK        | 成功           |
| 404 Not Found | 数据空间不存在 |

---

## Drop Table

`POST /api/v1/data-spaces/{datasourceId}/drop-table`

删除数据空间中的指定表。

### Path Parameters

| Name         | Type    | Description |
| ------------ | ------- | ----------- |
| datasourceId | integer | 数据源 ID   |

### Request Body

```json
{
  "tableName": "string"
}
```

| Field     | Type   | Validation | Description |
| --------- | ------ | ---------- | ----------- |
| tableName | string | required   | 表名        |

### Responses

| Status        | Description    |
| ------------- | -------------- |
| 200 OK        | 删除成功       |
| 404 Not Found | 数据空间不存在 |

---

## Insert Rows

`POST /api/v1/data-spaces/{datasourceId}/insert-rows`

向数据空间的表中插入行数据（事务性写入）。

### Path Parameters

| Name         | Type    | Description |
| ------------ | ------- | ----------- |
| datasourceId | integer | 数据源 ID   |

### Request Body

```json
{
  "tableName": "string",
  "columns": ["col1", "col2"],
  "rows": [
    ["value1", 123],
    ["value2", 456]
  ]
}
```

| Field     | Type          | Validation      | Description                       |
| --------- | ------------- | --------------- | --------------------------------- |
| tableName | string        | required        | 表名                              |
| columns   | array[string] | required, min=1 | 要插入数据的列名列表              |
| rows      | array[array]  | required, min=1 | 数据行，每行按 columns 顺序对应值 |

### 行为说明

- 插入操作在一个数据库事务中执行：任一插入失败则全部回滚
- `map[string]any` 类型的值会自动 JSON 序列化为字符串

### Responses

| Status          | Description    |
| --------------- | -------------- |
| 200 OK          | 插入成功       |
| 400 Bad Request | 表不存在       |
| 404 Not Found   | 数据空间不存在 |

---

## 通用错误

所有接口均可能返回以下错误：

| Status                    | Description          |
| ------------------------- | -------------------- |
| 401 Unauthorized          | 未认证               |
| 403 Forbidden             | 无权限（非表所有者） |
| 500 Internal Server Error | 服务器内部错误       |
