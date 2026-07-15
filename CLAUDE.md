# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **`AGENTS.md` is the authoritative agent guide for this repo** — read it for the full skill table, critical must-follow rules, developer commands, and editing guidance. This file summarizes the big-picture architecture; AGENTS.md has the details.

## What this repo is

A **content repository** of AI agent skills for the [Datadata](https://www.datadata.com) analytics platform — no build system, no tests, no toolchain. The deliverables are Markdown skill files. Each skill lives under `skills/<name>/` with a `SKILL.md` (YAML frontmatter + instructions) and a `references/` folder of deep-dive docs that `SKILL.md` links to. Skills are consumed by Claude Code and Codex via `npx skills add`.

Skills and docs are written in **Chinese** (frontmatter `description` fields carry an English half for skill routing). Match the existing language when editing.

## The four skills and how they divide up

The central architectural decision is a **two-axis split**: interactive-vs-scripted, and read-vs-write.

- **`datadata-manual`** — interactive operations via the Datadata **MCP Server** (OAuth, no API key). This is the *default* for anything done in-chat: searching data sources, querying, exploring metadata, managing Data Spaces.
- **`datadata-rest-api`** — the REST API reference, used to **generate standalone Python scripts** (crawlers, ETL, batch/cron jobs). Same operations as manual, but as `urllib.request` code instead of MCP calls. Requires an API key.
- **`datadata-dql`** — reference for writing **DQL** scripts (a Starlark dialect) for data transformation. Both manual and rest-api can execute DQL; this skill is the language/API reference.
- **`datadata-memory`** — persistent AI memory (add / search / update / delete) via MCP.

Two rules that recur across manual and rest-api and are easy to get wrong:

- **Read/write separation**: `execute-adhoc` is **read-only SELECT** (data sources, including dataspaces, are mounted read-only). All writes/DDL to a dataspace go through the dataspace SQL execute path — `dataspace-execute-sql` (MCP) or `POST /dataspaces/{id}/execute` (REST), which runs arbitrary DuckDB SQL synchronously.
- **Never auto-pick a data source**: `search-datasource` results must be presented as a numbered list for the user to choose — even a single result needs confirmation. And follow the *minimal-operation* rule: do exactly the one step asked, then stop; don't chain follow-up exploration.

Terminology note: the dataspace datasource type is `dataspace`; the old name `ducklake` is deprecated. When touching dataspace docs, keep both `datadata-manual` and `datadata-rest-api` references in sync.

## Working on this repo

- **Installing a skill locally to test** (from AGENTS.md): `npx skills add ./skills/<name> --agent claude-code --global` (or `--agent codex`).
- **DQL source of truth**: `skills/datadata-dql/references/__builtins__.pyi` defines all built-in signatures. Every DQL built-in is a global — no `import`. When editing DQL docs, keep the `.pyi` and the `.md` reference files in sync.
- **When MCP tools or API endpoints change**, update the corresponding skill: MCP tool changes → `skills/datadata-manual/SKILL.md`; endpoint changes → `skills/datadata-rest-api/references/api.md`.
- **Commits**: AngularJS-style conventional commits with Chinese descriptions (the parent workspace convention adds emoji, e.g. `refactor(dataspaces): ...`). Editor config is 2-space / LF / UTF-8; Markdown does not word-wrap.
