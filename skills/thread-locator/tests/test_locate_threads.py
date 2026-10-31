import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parents[1] / "scripts"
import sys

sys.path.insert(0, str(SCRIPT_DIR))
import locate_threads


CODEX_ID = "01a05799-4282-7ac2-8f54-819738412b3c"
CURSOR_ID = "fbef070a-c8e6-4359-b8ef-806e1c96fee5"
CLAUDE_ID = "8e01ed78-a864-4919-b9ac-14efde9b1b98"
CLAUDE_THREAD = "cmsg_01CkeHYnsC5EpJhNbLYB62Pu1x2yhcMn2C2wFgrMFD7442"


class LocateThreadsTest(unittest.TestCase):
    def write_claude(self, root, session_id, rows, filename=None):
        path = root / "projects/example" / (filename or f"{session_id}.jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(json.dumps({"sessionId": session_id, **row}) for row in rows) + "\n", encoding="utf-8")
        return path

    def test_claude_thread_id_selects_provider_and_preserves_case(self):
        self.assertEqual(("claude", CLAUDE_THREAD, "thread_id"), locate_threads.parse_input(CLAUDE_THREAD))
        with self.assertRaises(ValueError):
            locate_threads.locate(CLAUDE_THREAD, source="codex")

    def test_claude_thread_owner_precedes_quoted_reference_at_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_claude(root, CODEX_ID, [
                {"type": "user", "message": {"content": f'<relay><cited thread="{CLAUDE_THREAD}">quoted</cited></relay>'}},
            ])
            path = self.write_claude(root, CLAUDE_ID, [
                {"type": "user", "cwd": "/tmp/ayme", "gitBranch": "inspector", "timestamp": "2026-09-26T14:10:42Z",
                 "message": {"content": f'<wake reason="mention"><project><thread ts="{CLAUDE_THREAD}"><message>proceed</message></thread></project></wake>'}},
                {"type": "custom-title", "customTitle": "Inspector rebuild"},
            ])
            result = locate_threads.locate(CLAUDE_THREAD, claude_root=root)
            self.assertEqual(["claude"], result["searched"])
            owner, reference = result["matches"]
            self.assertEqual("exact_thread_id", owner["match"])
            self.assertEqual(CLAUDE_ID, owner["id"])
            self.assertEqual(CLAUDE_THREAD, owner["thread_id"])
            self.assertEqual([str(path)], owner["segments"])
            self.assertEqual("Inspector rebuild", owner["title"])
            self.assertEqual("/tmp/ayme", owner["cwd"])
            self.assertEqual("inspector", owner["branch"])
            self.assertIsNone(owner["archived"])
            self.assertEqual("thread_reference", reference["match"])
            limited = locate_threads.locate(CLAUDE_THREAD, claude_root=root, limit=1)
            self.assertEqual(CLAUDE_ID, limited["matches"][0]["id"])

    def test_claude_assistant_quote_is_only_a_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_claude(root, CLAUDE_ID, [{"type": "assistant", "message": {"content": [
                {"type": "text", "text": f'<wake reason="mention"><thread ts="{CLAUDE_THREAD}">example</thread></wake>'},
            ]}}])
            result = locate_threads.locate(CLAUDE_THREAD, claude_root=root)
            self.assertEqual("thread_reference", result["matches"][0]["match"])

    def test_claude_thread_id_does_not_match_a_longer_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_claude(root, CLAUDE_ID, [{"type": "user", "message": {"content": CLAUDE_THREAD + "extra"}}])
            result = locate_threads.locate(CLAUDE_THREAD, claude_root=root)
            self.assertEqual([], result["matches"])

    def test_claude_project_message_envelope_identifies_owner(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_claude(root, CLAUDE_ID, [{"type": "user", "message": {"content":
                f'<project_claude_message session="example" thread_id="{CLAUDE_THREAD}">hello</project_claude_message>'}}])
            result = locate_threads.locate(CLAUDE_THREAD, claude_root=root)
            self.assertEqual("exact_thread_id", result["matches"][0]["match"])

    def test_claude_session_id_groups_segments(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for filename in ("segment-a.jsonl", "segment-b.jsonl"):
                self.write_claude(root, CLAUDE_ID, [{"type": "user", "message": {"content": "hello"}}], filename)
            result = locate_threads.locate(CLAUDE_ID.upper(), source="claude", claude_root=root)
            self.assertEqual(1, len(result["matches"]))
            self.assertEqual(CLAUDE_ID, result["matches"][0]["id"])
            self.assertEqual(2, len(result["matches"][0]["segments"]))

    def test_claude_text_search_excludes_thinking_and_tool_payloads(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_claude(root, CLAUDE_ID, [{"type": "assistant", "message": {"content": [
                {"type": "thinking", "thinking": "secret phrase"},
                {"type": "tool_use", "input": {"text": "secret phrase"}},
                {"type": "text", "text": "Inspector redesign"},
            ]}}])
            found = locate_threads.locate("inspector redesign", source="claude", claude_root=root)
            self.assertEqual(CLAUDE_ID, found["matches"][0]["id"])
            hidden = locate_threads.locate("secret phrase", source="claude", claude_root=root)
            self.assertEqual([], hidden["matches"])

    def test_claude_missing_store_and_malformed_records_report_warnings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            missing = locate_threads.locate(CLAUDE_ID, source="claude", claude_root=root)
            self.assertEqual([], missing["matches"])
            self.assertTrue(missing["warnings"])
            path = self.write_claude(root, CLAUDE_ID, [{"type": "user", "message": {"content": "hello"}}])
            with path.open("a") as stream:
                stream.write("{broken\n")
            found = locate_threads.locate(CLAUDE_ID, source="claude", claude_root=root)
            self.assertEqual(CLAUDE_ID, found["matches"][0]["id"])
            self.assertIn("1 malformed", found["warnings"][0])

    def test_normalizes_urls_and_bare_ids(self):
        self.assertEqual(("codex", CODEX_ID, "id"), locate_threads.parse_input(f"codex://threads/{CODEX_ID}"))
        self.assertEqual((None, CURSOR_ID, "id"), locate_threads.parse_input(CURSOR_ID.upper()))
        with self.assertRaises(ValueError):
            locate_threads.parse_input("cursor://threads/00000000-0000-0000-0000-00000000000z")

    def test_finds_codex_id_and_groups_segments(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / ".codex"
            sessions = root / "sessions/2026/09/01"
            sessions.mkdir(parents=True)
            (root / "session_index.jsonl").write_text(
                json.dumps({"id": CODEX_ID, "thread_name": "Example", "updated_at": "2026-09-01T00:00:00Z"}) + "\n",
                encoding="utf-8",
            )
            for suffix in ("a", "b"):
                (sessions / f"rollout-{CODEX_ID}-{suffix}.jsonl").write_text(
                    json.dumps({"payload": {"id": CODEX_ID, "session_id": CODEX_ID, "cwd": "/tmp/example"}}) + "\n",
                    encoding="utf-8",
                )
            result = locate_threads.locate(CODEX_ID, source="codex", codex_root=root)
            self.assertEqual([CODEX_ID], [row["id"] for row in result["matches"]])
            self.assertEqual(2, len(result["matches"][0]["segments"]))

    def test_finds_cursor_id_from_sqlite(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "conversation-search.db"
            connection = sqlite3.connect(database)
            connection.execute(
                "CREATE TABLE conversations (source TEXT, scope TEXT, id TEXT, title TEXT, branches TEXT, updated_at INTEGER, is_archived INTEGER, fts_rowid INTEGER)"
            )
            connection.execute(
                "INSERT INTO conversations VALUES ('local', '', ?, 'Example', 'main', 1788264542492, 0, 1)",
                (CURSOR_ID,),
            )
            connection.commit()
            connection.close()
            result = locate_threads.locate(CURSOR_ID, source="cursor", cursor_database=database)
            self.assertEqual([CURSOR_ID], [row["id"] for row in result["matches"]])


if __name__ == "__main__":
    unittest.main()
