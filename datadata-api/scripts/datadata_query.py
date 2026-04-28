#!/usr/bin/env python3
"""Execute scripts against Datadata and fetch execution results."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=os.environ.get("DATADATA_BASE_URL", "https://www.datadata.com/api/v1"))
    parser.add_argument("--api-key", default=os.environ.get("DATADATA_API_KEY"))
    subparsers = parser.add_subparsers(dest="command", required=True)

    datasource_info_parser = subparsers.add_parser("get-datasource-info", help="Fetch datasource metadata.")
    datasource_info_parser.add_argument("--datasource-id", required=True)

    list_tables_parser = subparsers.add_parser("list-tables", help="List tables for a datasource.")
    list_tables_parser.add_argument("--datasource-id", required=True)
    list_tables_parser.add_argument("--schema-name")

    describe_table_parser = subparsers.add_parser("describe-table", help="Describe a table for a datasource.")
    describe_table_parser.add_argument("--datasource-id", required=True)
    describe_table_parser.add_argument("--schema-name", required=True)
    describe_table_parser.add_argument("--table-name", required=True)

    execute_parser = subparsers.add_parser("execute-adhoc", help="Create an adhoc execution from a script.")
    execute_parser.add_argument("--script-type", default="sql")
    execute_parser.add_argument("--query-engine", default="duckdb")
    execute_parser.add_argument(
        "--datasource",
        action="append",
        default=[],
        metavar="DATASOURCE_ID:ATTACH_ALIAS",
        help="Bind a datasource to the adhoc query. Repeat for multiple datasources.",
    )
    execute_parser.add_argument("--script", required=True)

    result_parser = subparsers.add_parser("get-execution-result", help="Fetch a result artifact for an execution.")
    result_parser.add_argument("--execution-id", required=True)
    result_parser.add_argument(
        "--format",
        choices=("ndjson", "csv"),
        default="ndjson",
        help="Result format to download for the execution ID.",
    )
    result_parser.add_argument("--output-path")
    return parser.parse_args()


def build_url(base_url: str, path: str, query: dict[str, str] | None = None) -> str:
    base = base_url.rstrip("/")
    url = f"{base}{path}"
    if query:
        url = f"{url}?{urllib.parse.urlencode(query)}"
    return url


def fetch_datasource_info(base_url: str, api_key: str, datasource_id: str) -> Any:
    return request_json(build_url(base_url, f"/datasources/{datasource_id}/info"), api_key)


def fetch_list_tables(base_url: str, api_key: str, datasource_id: str, schema_name: str | None) -> Any:
    query = {"schemaName": schema_name} if schema_name else None
    return request_json(build_url(base_url, f"/datasources/{datasource_id}/list-tables", query), api_key)


def fetch_describe_table(base_url: str, api_key: str, datasource_id: str, schema_name: str, table_name: str) -> Any:
    query = {
        "schemaName": schema_name,
        "tableName": table_name,
    }
    return request_json(build_url(base_url, f"/datasources/{datasource_id}/describe-table", query), api_key)


def request_json(url: str, api_key: str, method: str = "GET", payload: dict[str, Any] | None = None) -> Any:
    data = None
    headers = {
        "X-Datadata-Api-key": api_key,
        "Accept": "application/json",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            content_type = resp.headers.get("Content-Type", "")
            if not raw:
                return None
            if "application/x-ndjson" in content_type:
                return parse_ndjson(raw)
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc


def request_text(url: str, api_key: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"X-Datadata-Api-key": api_key, "Accept": "*/*"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc


def request_bytes(url: str, api_key: str) -> tuple[bytes, str]:
    req = urllib.request.Request(
        url,
        headers={"X-Datadata-Api-key": api_key, "Accept": "*/*"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read(), resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc


def parse_ndjson(raw: str) -> list[Any]:
    rows = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def parse_datasource_bindings(values: list[str]) -> list[dict[str, str]]:
    bindings = []
    for raw in values:
        datasource_id, sep, attach_alias = raw.partition(":")
        datasource_id = datasource_id.strip()
        attach_alias = attach_alias.strip()
        if not sep or not datasource_id or not attach_alias:
            raise ValueError(
                f"Invalid --datasource value '{raw}'. Use DATASOURCE_ID:ATTACH_ALIAS."
            )
        bindings.append(
            {
                "datasourceId": datasource_id,
                "attachAlias": attach_alias,
            }
        )
    return bindings


def find_execution_id(payload: Any) -> str | None:
    if isinstance(payload, dict):
        value = payload.get("id")
        if isinstance(value, str) and value:
            return value
        for key in ("executionId", "execution_id"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
        for value in payload.values():
            found = find_execution_id(value)
            if found:
                return found
    elif isinstance(payload, list):
        for item in payload:
            found = find_execution_id(item)
            if found:
                return found
    return None


def create_execution(
    base_url: str,
    api_key: str,
    script: str,
    script_type: str,
    query_engine: str,
    datasources: list[dict[str, str]],
) -> tuple[str, Any]:
    payload = {
        "script": script,
        "scriptType": script_type,
        "queryEngine": query_engine,
    }
    if datasources:
        payload["datasources"] = datasources
    response = request_json(
        build_url(base_url, "/queries/execute-adhoc"),
        api_key,
        method="POST",
        payload=payload,
    )
    execution_id = find_execution_id(response)
    if not execution_id:
        raise RuntimeError(
            "Could not find executionId in create-query response.\n"
            f"Raw response: {json.dumps(response, ensure_ascii=False)}"
        )
    return execution_id, response


def fetch_result_artifact(base_url: str, api_key: str, execution_id: str, fmt: str) -> tuple[bytes, str]:
    url = build_url(base_url, f"/executions/{execution_id}/result", {"format": fmt})
    if fmt == "csv":
        text = request_text(url, api_key)
        return text.encode("utf-8"), "text/csv"
    return request_bytes(url, api_key)


def default_output_path(execution_id: str, fmt: str, content_type: str) -> str:
    suffix = ".json"
    if fmt == "ndjson" or "application/x-ndjson" in content_type:
        suffix = ".ndjson"
    elif fmt == "csv":
        suffix = ".csv"
    return os.path.join(tempfile.gettempdir(), f"datadata-{execution_id}{suffix}")


def write_artifact(path: str, content: bytes) -> dict[str, Any]:
    with open(path, "wb") as fh:
        fh.write(content)
    return {
        "outputPath": path,
        "bytes": len(content),
    }


def estimate_rows(content: bytes, content_type: str) -> int | None:
    if "application/x-ndjson" not in content_type:
        return None
    return sum(1 for line in content.splitlines() if line.strip())


def require_common_args(args: argparse.Namespace) -> int:
    if not args.base_url:
        print("Missing --base-url or DATADATA_BASE_URL", file=sys.stderr)
        return 2
    if not args.api_key:
        print("Missing --api-key or DATADATA_API_KEY", file=sys.stderr)
        return 2
    return 0


def run_execute_adhoc(args: argparse.Namespace) -> int:
    try:
        datasources = parse_datasource_bindings(args.datasource)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    execution_id, create_response = create_execution(
        args.base_url,
        args.api_key,
        args.script,
        args.script_type,
        args.query_engine,
        datasources,
    )
    print(
        json.dumps(
            {
                "executionId": execution_id,
                "execution": create_response,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def run_get_datasource_info(args: argparse.Namespace) -> int:
    response = fetch_datasource_info(args.base_url, args.api_key, args.datasource_id)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


def run_list_tables(args: argparse.Namespace) -> int:
    response = fetch_list_tables(args.base_url, args.api_key, args.datasource_id, args.schema_name)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


def run_describe_table(args: argparse.Namespace) -> int:
    response = fetch_describe_table(
        args.base_url,
        args.api_key,
        args.datasource_id,
        args.schema_name,
        args.table_name,
    )
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


def run_get_execution_result(args: argparse.Namespace) -> int:
    try:
        result = fetch_result_artifact(args.base_url, args.api_key, args.execution_id, args.format)
    except Exception as exc:  # noqa: BLE001
        print(
            json.dumps(
                {
                    "executionId": args.execution_id,
                    "fetchError": str(exc),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    content, content_type = result
    output_path = args.output_path or default_output_path(args.execution_id, args.format, content_type)
    artifact = write_artifact(output_path, content)
    artifact["contentType"] = content_type or ("text/csv" if args.format == "csv" else "application/x-ndjson")
    artifact["format"] = args.format
    row_count = estimate_rows(content, artifact["contentType"])
    if row_count is not None:
        artifact["rowCount"] = row_count
    print(
        json.dumps(
            {
                "executionId": args.execution_id,
                "result": artifact,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def main() -> int:
    args = parse_args()
    code = require_common_args(args)
    if code:
        return code
    if args.command == "get-datasource-info":
        return run_get_datasource_info(args)
    if args.command == "list-tables":
        return run_list_tables(args)
    if args.command == "describe-table":
        return run_describe_table(args)
    if args.command == "execute-adhoc":
        return run_execute_adhoc(args)
    if args.command == "get-execution-result":
        return run_get_execution_result(args)
    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
