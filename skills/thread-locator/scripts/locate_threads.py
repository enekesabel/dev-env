#!/usr/bin/env python3
"""Locate Codex, Cursor and Claude threads from their local read-only stores."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
URL_RE = re.compile(
    r"^(codex|cursor)://threads/([0-9a-f-]{36})/?$", re.IGNORECASE
)
TOKEN_RE = re.compile(r"[0-9A-Za-z_]+")
CLAUDE_THREAD_RE = re.compile(r"^cmsg_[0-9A-Za-z]+$")


def iso_timestamp(value: Any, milliseconds: bool = False) -> str | None:
    if value is None:
        return None
    try:
        seconds = float(value) / (1000 if milliseconds else 1)
        return datetime.fromtimestamp(seconds, timezone.utc).isoformat()
    except (TypeError, ValueError, OSError, OverflowError):
        return None


def parse_input(value: str) -> tuple[str | None, str, str | None]:
    text = value.strip()
    match = URL_RE.fullmatch(text)
    if match:
        thread_id = match.group(2).lower()
        if not UUID_RE.fullmatch(thread_id):
            raise ValueError("thread URL must contain a valid UUID")
        return match.group(1).lower(), thread_id, "id"
    if UUID_RE.fullmatch(text):
        return None, text.lower(), "id"
    if CLAUDE_THREAD_RE.fullmatch(text):
        return "claude", text, "thread_id"
    if text.lower().startswith(("codex://", "cursor://")):
        raise ValueError("thread URL must look like <provider>://threads/<uuid>")
    if not text:
        raise ValueError("query cannot be empty")
    return None, text, "text"


def read_codex_index(root: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    path = root / "session_index.jsonl"
    entries: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []
    if not path.is_file():
        return entries, [f"Codex index not found: {path}"]
    try:
        with path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                try:
                    row = json.loads(line)
                    thread_id = str(row["id"]).lower()
                    entries[thread_id] = row
                except (KeyError, TypeError, json.JSONDecodeError):
                    warnings.append(f"Skipped malformed Codex index row {line_number}")
    except OSError as error:
        warnings.append(f"Could not read Codex index {path}: {error}")
    return entries, warnings


def codex_segment_paths(root: Path, thread_id: str) -> list[Path]:
    paths: list[Path] = []
    for directory in (root / "sessions", root / "archived_sessions"):
        if directory.is_dir():
            paths.extend(path for path in directory.rglob(f"*{thread_id}*.jsonl") if path.is_file())
    return sorted(set(paths))


def read_codex_meta(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as stream:
            row = json.loads(stream.readline())
        payload = row.get("payload", {})
        return payload if isinstance(payload, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def codex_record(
    root: Path,
    thread_id: str,
    index_row: dict[str, Any] | None,
    paths: list[Path],
) -> dict[str, Any]:
    index_row = index_row or {}
    meta = read_codex_meta(paths[0]) if paths else {}
    git = meta.get("git") if isinstance(meta.get("git"), dict) else {}
    updated_values = [
        path.stat().st_mtime for path in paths if path.exists()
    ]
    if index_row.get("updated_at"):
        try:
            updated_values.append(
                datetime.fromisoformat(str(index_row["updated_at"]).replace("Z", "+00:00")).timestamp()
            )
        except (TypeError, ValueError, OSError):
            pass
    updated = iso_timestamp(max(updated_values)) if updated_values else index_row.get("updated_at")
    archived = any("archived_sessions" in path.parts for path in paths)
    return {
        "provider": "codex",
        "id": thread_id,
        "title": index_row.get("thread_name"),
        "updated_at": updated,
        "archived": archived,
        "cwd": meta.get("cwd"),
        "branch": None,
        "repository": git.get("repository_url"),
        "reference": f"codex://threads/{thread_id}",
        "match": "exact_id" if paths or index_row else "text",
        "segments": [str(path) for path in paths],
        "evidence": str(root / "session_index.jsonl"),
    }


def find_codex_exact(root: Path, thread_id: str) -> tuple[list[dict[str, Any]], list[str]]:
    entries, warnings = read_codex_index(root)
    paths = codex_segment_paths(root, thread_id)
    if thread_id not in entries and not paths:
        return [], warnings
    return [codex_record(root, thread_id, entries.get(thread_id), paths)], warnings


def find_codex_titles(root: Path, query: str, limit: int) -> tuple[list[dict[str, Any]], list[str]]:
    entries, warnings = read_codex_index(root)
    normalized = query.casefold().strip()
    tokens = [token.casefold() for token in TOKEN_RE.findall(query)]
    matches: list[tuple[int, str, dict[str, Any]]] = []
    for thread_id, row in entries.items():
        title = str(row.get("thread_name") or "")
        lowered = title.casefold()
        if normalized and normalized in lowered:
            score = 0
        elif tokens and all(token in lowered for token in tokens):
            score = 1
        else:
            continue
        record = codex_record(root, thread_id, row, codex_segment_paths(root, thread_id))
        record["match"] = "exact_title" if score == 0 else "title_tokens"
        matches.append((score, thread_id, record))
    matches.sort(key=lambda item: (item[0], item[1]))
    return [record for _, _, record in matches[:limit]], warnings


def cursor_connection(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)


def cursor_record(row: sqlite3.Row, database: Path, match: str) -> dict[str, Any]:
    return {
        "provider": "cursor",
        "id": row["id"],
        "title": row["title"],
        "updated_at": iso_timestamp(row["updated_at"], milliseconds=True),
        "archived": bool(row["is_archived"]),
        "cwd": None,
        "branch": row["branches"] or None,
        "repository": None,
        "reference": row["id"],
        "match": match,
        "scope": row["scope"],
        "source": row["source"],
        "evidence": str(database),
    }


def find_cursor(
    database: Path, query: str, kind: str, limit: int
) -> tuple[list[dict[str, Any]], list[str]]:
    if not database.is_file():
        return [], [f"Cursor conversation index not found: {database}"]
    warnings: list[str] = []
    try:
        connection = cursor_connection(database)
    except sqlite3.Error as error:
        return [], [f"Could not open Cursor conversation index: {error}"]
    connection.row_factory = sqlite3.Row
    try:
        if kind == "id":
            rows = connection.execute(
                """
                SELECT source, scope, id, title, branches, updated_at, is_archived
                FROM conversations
                WHERE lower(id) = lower(?)
                ORDER BY updated_at DESC, source, scope, id
                LIMIT ?
                """,
                (query, limit),
            ).fetchall()
            return [cursor_record(row, database, "exact_id") for row in rows], warnings

        tokens = TOKEN_RE.findall(query)
        if not tokens:
            return [], ["Text query contains no searchable words"]
        fts_query = " AND ".join(f'"{token}"' for token in tokens)
        rows = connection.execute(
            """
            SELECT c.source, c.scope, c.id, c.title, c.branches, c.updated_at, c.is_archived
            FROM conversations AS c
            JOIN conversation_fts ON conversation_fts.rowid = c.fts_rowid
            WHERE conversation_fts MATCH ?
            ORDER BY c.updated_at DESC, c.source, c.scope, c.id
            LIMIT ?
            """,
            (fts_query, limit),
        ).fetchall()
        return [cursor_record(row, database, "text") for row in rows], warnings
    except sqlite3.Error as error:
        warnings.append(f"Cursor search failed: {error}")
        return [], warnings
    finally:
        connection.close()


def claude_text(row: dict[str, Any]) -> str:
    message = row.get("message")
    if not isinstance(message, dict):
        return ""
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "") for block in content
            if isinstance(block, dict) and block.get("type") == "text" and isinstance(block.get("text"), str)
        )
    return ""


def find_claude(
    root: Path, query: str, kind: str, limit: int
) -> tuple[list[dict[str, Any]], list[str]]:
    projects = root / "projects"
    if not projects.is_dir():
        return [], [f"Claude transcripts not found: {projects}"]
    matches: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []
    rank = {"exact_id": 0, "exact_thread_id": 0, "text": 1, "thread_reference": 2}
    tokens = [token.casefold() for token in TOKEN_RE.findall(query)]
    id_pattern = re.compile(r"(?<![0-9A-Za-z_])" + re.escape(query) + r"(?![0-9A-Za-z_])")
    thread_pattern = re.compile(
        r'<thread\s+[^>]*\bts=[\'\"]' + re.escape(query) + r'[\'\"]'
        r'|^<project_claude_message\s+[^>]*\bthread_id=[\'\"]' + re.escape(query) + r'[\'\"]'
    )
    for path in sorted(projects.rglob("*.jsonl")):
        session_id = path.stem
        title = cwd = branch = updated = None
        match = None
        malformed = 0
        try:
            with path.open(encoding="utf-8") as stream:
                for line in stream:
                    try:
                        row = json.loads(line)
                        if not isinstance(row, dict):
                            raise ValueError("record is not an object")
                    except (ValueError, TypeError):
                        malformed += 1
                        continue
                    session_id = row.get("sessionId") or session_id
                    cwd = row.get("cwd") or cwd
                    branch = row.get("gitBranch") or branch
                    updated = row.get("timestamp") or updated
                    if row.get("type") == "custom-title":
                        title = row.get("customTitle") or title
                    candidate = None
                    if kind == "id" and str(session_id).lower() == query:
                        candidate = "exact_id"
                    elif kind == "thread_id" and id_pattern.search(line):
                        candidate = "thread_reference"
                        text = claude_text(row).strip() if row.get("type") == "user" else ""
                        if (text.startswith("<wake ") or text.startswith("<project_claude_message ")) and thread_pattern.search(text):
                            candidate = "exact_thread_id"
                    elif kind == "text":
                        text = claude_text(row) if row.get("type") in ("user", "assistant") else ""
                        searchable = "\n".join(str(value or "") for value in (title, cwd, branch, text)).casefold()
                        if tokens and all(token in searchable for token in tokens):
                            candidate = "text"
                    if candidate and (match is None or rank[candidate] < rank[match]):
                        match = candidate
        except (OSError, UnicodeError) as error:
            warnings.append(f"Could not read Claude transcript {path}: {error}")
            continue
        if malformed:
            warnings.append(f"Skipped {malformed} malformed Claude records in {path}")
        if match is None:
            continue
        record = {
            "provider": "claude", "id": session_id,
            "thread_id": query if kind == "thread_id" else None,
            "title": title, "updated_at": updated, "archived": None,
            "cwd": cwd, "branch": branch, "repository": None,
            "reference": session_id, "match": match,
            "segments": [str(path)], "evidence": str(path),
        }
        existing = matches.get(session_id)
        if existing:
            record["segments"] = existing["segments"] + record["segments"]
            record["updated_at"] = max(filter(None, (existing["updated_at"], updated)), default=None)
            for field in ("title", "cwd", "branch"):
                record[field] = record[field] or existing[field]
            if rank[existing["match"]] <= rank[match]:
                record["match"] = existing["match"]
        matches[session_id] = record
    ordered = sorted(matches.values(), key=lambda row: (rank[row["match"]], row["id"]))
    return ordered[:limit], warnings


def locate(
    query: str,
    source: str = "auto",
    limit: int = 20,
    codex_root: Path | None = None,
    cursor_database: Path | None = None,
    claude_root: Path | None = None,
) -> dict[str, Any]:
    forced_source, normalized, kind = parse_input(query)
    if forced_source and source != "auto" and source != forced_source:
        raise ValueError(f"input selects {forced_source}, but --source selects {source}")
    source = forced_source or source
    codex_root = codex_root or Path.home() / ".codex"
    cursor_database = cursor_database or Path.home() / "Library/Application Support/Cursor/User/globalStorage/conversation-search.db"
    claude_root = claude_root or Path.home() / ".claude"

    matches: list[dict[str, Any]] = []
    warnings: list[str] = []
    searched: list[str] = []
    if source in ("auto", "codex"):
        searched.append("codex")
        if kind == "id":
            found, errors = find_codex_exact(codex_root, normalized)
        else:
            found, errors = find_codex_titles(codex_root, normalized, limit)
        matches.extend(found)
        warnings.extend(errors)
    if source in ("auto", "cursor"):
        searched.append("cursor")
        found, errors = find_cursor(cursor_database, normalized, kind, limit)
        matches.extend(found)
        warnings.extend(errors)

    if source in ("auto", "claude"):
        searched.append("claude")
        found, errors = find_claude(claude_root, normalized, kind, limit)
        matches.extend(found)
        warnings.extend(errors)

    provider_order = {"codex": 0, "cursor": 1, "claude": 2}
    matches.sort(key=lambda row: (
        0 if row["match"].startswith("exact_") else 2 if row["match"] == "thread_reference" else 1,
        provider_order[row["provider"]], row["id"],
    ))
    return {
        "query": query,
        "searched": searched,
        "matches": matches[:limit],
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="thread URL, UUID, Claude cmsg ID, title, branch, or text")
    parser.add_argument("--source", choices=("auto", "codex", "cursor", "claude"), default="auto")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--codex-root", type=Path, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--cursor-database", type=Path, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--claude-root", type=Path, default=None, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.limit < 1:
        parser.error("--limit must be positive")
    try:
        result = locate(
            args.query,
            source=args.source,
            limit=args.limit,
            codex_root=args.codex_root,
            cursor_database=args.cursor_database,
            claude_root=args.claude_root,
        )
    except ValueError as error:
        parser.error(str(error))

    if args.json:
        print(json.dumps(result, indent=2))
    elif result["matches"]:
        for row in result["matches"]:
            context = row.get("branch") or row.get("cwd") or "-"
            print(f"{row['provider']:6} {row['id']}  {row.get('title') or '-'}  {context}")
            print(f"       {row['reference']}")
    else:
        print("No thread matches.")
    for warning in result["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)
    return 0 if result["matches"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
