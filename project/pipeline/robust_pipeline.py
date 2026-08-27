#!/usr/bin/env python3
"""Safe, resumable podcast production workflow.

The command line interface deliberately uses only the Python standard library.
It is designed to make the existing episode files inspectable and to keep
network publication outside the rendering step.
"""
from __future__ import annotations

import argparse
import asyncio
import contextlib
import hashlib
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
PIPELINE = ROOT / "pipeline"
LEDGER_PATH = PIPELINE / "state.json"
INVENTORY_PATH = PIPELINE / "inventory.json"
LOCK_PATH = PIPELINE / ".pipeline.lock"
MANIFEST_PATH = PIPELINE / "manifest.json"
FEED_BASE = "https://mrdavidgagnon.github.io/human-in-the-loop-AI-podcast"
REQUIRED_DISCLOSURE = "The complete citations are in the show notes, with links to the Zotero files when you have been granted access."
ROLES = {"host", "rowan", "guest"}
MAX_RETRIES = 4

STATES = {
    "planned", "review_pending", "reviewed", "rendering", "rendered",
    "verified", "published", "blocked", "failed",
}
TRANSITIONS = {
    "planned": {"review_pending", "blocked"},
    "review_pending": {"reviewed", "blocked"},
    "reviewed": {"rendering", "blocked"},
    "rendering": {"rendered", "failed", "blocked"},
    "rendered": {"verified", "rendering", "blocked"},
    "verified": {"published", "rendering", "blocked"},
    "published": {"rendering"},
    "blocked": {"review_pending", "planned"},
    "failed": {"rendering", "planned"},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def atomic_write(path: Path, content: str | bytes) -> None:
    """Write and fsync a file, then replace it so readers never see a half file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content.encode() if isinstance(content, str) else content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(name)


def atomic_json(path: Path, value: Any) -> None:
    atomic_write(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


class PipelineLock:
    """Exclusive process lock with an inspectable owner record.

    A lock is never silently broken: stale locks require an explicit
    ``unlock --force`` after a human has checked the owner record.
    """
    def __init__(self, path: Path = LOCK_PATH, timeout: float = 0.0):
        self.path, self.timeout, self.fd = path, timeout, None

    def __enter__(self):
        import fcntl
        self.path.parent.mkdir(parents=True, exist_ok=True)
        started = time.monotonic()
        self.fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o600)
        while True:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                owner = {"pid": os.getpid(), "host": socket.gethostname(), "started_at": utc_now(), "command": " ".join(sys.argv)}
                os.ftruncate(self.fd, 0)
                os.write(self.fd, json.dumps(owner).encode())
                os.fsync(self.fd)
                return self
            except BlockingIOError:
                if time.monotonic() - started >= self.timeout:
                    os.close(self.fd)
                    self.fd = None
                    raise RuntimeError(f"pipeline lock is held: {self.path}")
                time.sleep(0.05)

    def __exit__(self, *_):
        import fcntl
        if self.fd is not None:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
            self.fd = None


def unlock(force: bool = False) -> None:
    """Remove a lock record only when explicitly requested."""
    if not LOCK_PATH.exists():
        return
    if not force:
        raise RuntimeError("refusing to remove lock; use unlock --force after checking its owner")
    import fcntl
    fd = os.open(LOCK_PATH, os.O_RDWR)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("lock is currently held; refusing to remove an active lock")
        os.unlink(LOCK_PATH)
    finally:
        os.close(fd)


def lock_status(path: Path = LOCK_PATH) -> dict[str, Any]:
    """Report whether the persistent lock record is actively held."""
    if not path.exists():
        return {"present": False, "active": False}
    owner = {}
    with contextlib.suppress(Exception):
        owner = json.loads(path.read_text() or "{}")
    import fcntl
    fd = os.open(path, os.O_RDWR)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            active = False
            fcntl.flock(fd, fcntl.LOCK_UN)
        except BlockingIOError:
            active = True
    finally:
        os.close(fd)
    return {"present": True, "active": active, "owner": owner}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text())


def load_ledger() -> dict[str, Any]:
    if LEDGER_PATH.exists():
        data = json.loads(LEDGER_PATH.read_text())
        if data.get("schema_version") != 1:
            raise ValueError("unsupported pipeline state schema")
        return data
    manifest = load_manifest()
    episodes = {}
    for number, item in manifest.get("episodes", {}).items():
        manifest_status = str(item.get("status", ""))
        imported_status = "published" if manifest_status == "published_and_moved" else ("verified" if manifest_status.startswith("published_") else "planned")
        episodes[number] = {
            "status": imported_status,
            "sources": item.get("sources", []), "attempts": 0,
            "transitions": [{"from": None, "to": imported_status, "at": utc_now(), "reason": "imported from manifest"}],
            "checks": {}, "artifacts": {}, "errors": [],
        }
    return {"schema_version": 1, "pipeline": manifest.get("pipeline", "podcast"), "updated_at": utc_now(), "episodes": episodes}


def save_ledger(ledger: dict[str, Any]) -> None:
    ledger["updated_at"] = utc_now()
    atomic_json(LEDGER_PATH, ledger)


def transition(ledger: dict[str, Any], episode: str, to_state: str, reason: str = "") -> None:
    if to_state not in STATES:
        raise ValueError(f"unknown state: {to_state}")
    record = ledger.setdefault("episodes", {}).setdefault(episode, {"status": "planned", "transitions": []})
    old = record.get("status", "planned")
    if old != to_state and to_state not in TRANSITIONS.get(old, set()):
        raise ValueError(f"invalid state transition {episode}: {old} -> {to_state}")
    record["status"] = to_state
    record.setdefault("transitions", []).append({"from": old, "to": to_state, "at": utc_now(), "reason": reason})


def episode_dirs(episode: str | None = None) -> Iterable[tuple[str, Path]]:
    if episode:
        path = ROOT / "episodes" / episode
        if not path.is_dir():
            raise FileNotFoundError(path)
        return [(episode, path)]
    return sorted((p.name, p) for p in (ROOT / "episodes").iterdir() if p.is_dir() and p.name.isdigit())


def inventory(episode: str | None = None) -> dict[str, Any]:
    entries = []
    for number, directory in episode_dirs(episode):
        for path in sorted(directory.rglob("*")):
            if path.is_file() and not path.name.startswith("."):
                stat = path.stat()
                entries.append({"episode": number, "path": path.relative_to(ROOT).as_posix(), "size": stat.st_size, "sha256": sha256(path), "mtime_ns": stat.st_mtime_ns})
    ownership: dict[str, list[str]] = {}
    for number, item in load_manifest().get("episodes", {}).items():
        for key in item.get("sources", []):
            ownership.setdefault(key, []).append(number)
    result = {"schema_version": 1, "generated_at": utc_now(), "root": str(ROOT), "files": entries, "source_ownership": ownership,
              "duplicate_sources": {key: owners for key, owners in ownership.items() if len(owners) > 1}}
    atomic_json(INVENTORY_PATH, result)
    return result


def reconcile(episode: str | None = None, write: bool = False) -> dict[str, Any]:
    ledger = load_ledger()
    expected = load_manifest().get("episodes", {})
    report = {"generated_at": utc_now(), "episodes": {}, "ok": True}
    ownership: dict[str, list[str]] = {}
    for number, item in expected.items():
        for key in item.get("sources", []):
            ownership.setdefault(key, []).append(number)
    report["source_ownership"] = ownership
    for key, owners in ownership.items():
        if len(owners) > 1:
            report["ok"] = False
            report.setdefault("issues", []).append(f"source {key} is assigned to multiple episodes: {owners}")
    for number, directory in episode_dirs(episode):
        rec = ledger.setdefault("episodes", {}).setdefault(number, {"status": "planned", "transitions": []})
        expected_item = expected.get(number, {})
        audio = list(directory.glob("*.mp3"))
        notes = directory / "episode-notes.md"
        issues = []
        if expected_item.get("sources") and rec.get("sources") and sorted(expected_item["sources"]) != sorted(rec["sources"]):
            issues.append("ledger source list differs from manifest")
        if not notes.exists():
            issues.append("missing episode-notes.md")
        if rec.get("status") in {"rendered", "verified", "published"} and not audio:
            issues.append("ledger says audio exists but no MP3 is present")
        artifacts = {"notes": str(notes.relative_to(ROOT)) if notes.exists() else None,
                     "audio": [str(p.relative_to(ROOT)) for p in audio]}
        rec["artifacts"] = artifacts
        if issues:
            report["ok"] = False
            rec.setdefault("errors", []).extend(issues)
        report["episodes"][number] = {"status": rec.get("status"), "issues": issues, "artifacts": artifacts}
    if write:
        save_ledger(ledger)
    return report


def parse_turns(script: Path) -> list[tuple[str, str]]:
    turns = []
    for line in script.read_text().splitlines():
        m = re.match(r"^\*\*(Host|Rowan|Guest):\*\*\s+(.+?)\s*$", line, re.I)
        if m:
            role = m.group(1).lower().replace("guest", "rowan")
            if role not in ROLES or not m.group(2).strip():
                raise ValueError(f"invalid dialogue turn in {script}: {line}")
            turns.append((role, m.group(2).strip()))
    if not turns:
        raise ValueError(f"no Host/Rowan turns found in {script}")
    return turns


def source_keys(text: str) -> list[str]:
    return re.findall(r"(?:items/|zotero://select/items/)([A-Z0-9]{8})", text)


def review_gate(episode: str, panel: Path | None = None) -> dict[str, Any]:
    panel = panel or ROOT / "episodes" / episode / "review-panel.md"
    try:
        panel_label = str(panel.relative_to(ROOT))
    except ValueError:
        panel_label = str(panel)
    result: dict[str, Any] = {"episode": episode, "ok": False, "panel": panel_label, "issues": [], "reviewers": []}
    if not panel.exists():
        result["issues"].append("review panel is missing")
        return result
    text = panel.read_text()
    heading_matches = re.findall(r"^##\s+Reviewer\s+(\d+)\s+—\s+(.+)$", text, re.M)
    headings = [name for _, name in heading_matches]
    result["reviewers"] = headings
    if len(headings) != 3 or len(set(headings)) != 3 or len({number for number, _ in heading_matches}) != 3:
        result["issues"].append("exactly three distinct reviewer sections are required")
    verdicts = re.findall(r"(?:Initial\s+)?verdict:\s*([^\.\n]+)", text, re.I)
    if len(verdicts) != 3 or any("pass" not in v.lower() for v in verdicts):
        result["issues"].append("each reviewer must record a pass verdict")
    required = re.findall(r"Required revisions:\s*(.*?)(?=\n\n|\n##|$)", text, re.I | re.S)
    if len(required) != 3 or any(not r.strip() for r in required):
        result["issues"].append("each reviewer must record required revisions and their resolution")
    if not re.search(r"Revision record\b", text, re.I):
        result["issues"].append("revision record is missing")
    if re.search(r"\b(?:unresolved|not addressed|blocked)\b", text, re.I):
        result["issues"].append("panel contains an unresolved/blocking issue")
    result["ok"] = not result["issues"]
    return result


def record_review(episode: str, panel: Path | None = None) -> dict[str, Any]:
    """Persist a review decision and its evidence in the episode ledger."""
    result = review_gate(episode, panel)
    ledger = load_ledger()
    record = ledger.setdefault("episodes", {}).setdefault(episode, {"status": "planned", "transitions": []})
    record.setdefault("checks", {})["review_gate"] = result
    if result["ok"]:
        if record.get("status") == "planned":
            transition(ledger, episode, "review_pending", "review submitted")
        if record.get("status") == "review_pending":
            transition(ledger, episode, "reviewed", "three-reviewer gate passed")
    elif record.get("status") == "planned":
        transition(ledger, episode, "review_pending", "review gate failed; revisions required")
    save_ledger(ledger)
    return result


def preflight(episode: str, require_audio: bool = False, enforce_review: bool = True) -> dict[str, Any]:
    directory = ROOT / "episodes" / episode
    result: dict[str, Any] = {"episode": episode, "ok": False, "issues": [], "checks": {}}
    manifest = load_manifest().get("episodes", {}).get(episode, {})
    script, notes = directory / "script.md", directory / "episode-notes.md"
    try:
        turns = parse_turns(script)
        result["checks"]["dialogue_turns"] = len(turns)
    except (OSError, ValueError) as exc:
        result["issues"].append(str(exc))
        turns = []
    if not notes.exists():
        result["issues"].append("missing episode-notes.md")
        notes_text = ""
    else:
        notes_text = notes.read_text()
    script_text = script.read_text() if script.exists() else ""
    if REQUIRED_DISCLOSURE not in script_text and REQUIRED_DISCLOSURE not in notes_text:
        result["issues"].append("required Zotero-links disclosure is absent from both script and notes")
    if not re.search(r"fictional.*(?:composite|correspondent)|(?:composite|fictional).*correspondent", script_text, re.I | re.S):
        result["issues"].append("fictional-correspondent disclosure is absent from script")
    if not re.search(r"AI-generated|AI generated", script_text, re.I):
        result["issues"].append("AI-summary disclosure is absent from script")
    keys = source_keys(notes_text)
    expected_keys = list(manifest.get("sources", []))
    result["checks"]["notes_zotero_keys"] = sorted(set(keys))
    all_owners: dict[str, list[str]] = {}
    for number, item in load_manifest().get("episodes", {}).items():
        for key in item.get("sources", []):
            all_owners.setdefault(key, []).append(number)
    for key in expected_keys:
        if len(all_owners.get(key, [])) > 1:
            result["issues"].append(f"source {key} is assigned to multiple episodes")
    if expected_keys and not set(expected_keys).issubset(keys):
        result["issues"].append("manifest source key missing from episode notes")
    numbered = re.findall(r"^\s*\d+\.\s+(.+)$", notes_text, re.M)
    for key in expected_keys:
        entry = next((line for line in numbered if key in line), "")
        if not entry:
            result["issues"].append(f"source {key} has no numbered citation entry")
            continue
        if not re.search(r"\b(?:19|20)\d{2}\b", entry):
            result["issues"].append(f"source {key} citation has no publication year")
        if len(re.sub(r"\[[^]]+\]\([^)]*\)", "", entry).split()) < 8:
            result["issues"].append(f"source {key} citation is too short for author/title/venue metadata")
        if not re.search(r"zotero\.org|zotero://", entry, re.I):
            result["issues"].append(f"source {key} citation has no direct Zotero link")
    result["checks"]["numbered_source_entries"] = len(numbered)
    if len(keys) != len(set(keys)):
        result["issues"].append("duplicate Zotero links in notes")
    if enforce_review:
        gate = review_gate(episode)
        result["checks"]["review_gate"] = gate
        if not gate["ok"]:
            result["issues"].extend("review gate: " + issue for issue in gate["issues"])
    if require_audio:
        audio = list(directory.glob("*.mp3"))
        if len(audio) != 1 or audio[0].stat().st_size == 0:
            result["issues"].append("exactly one non-empty episode MP3 is required")
        else:
            result["checks"]["audio"] = {"path": str(audio[0].relative_to(ROOT)), "size": audio[0].stat().st_size, "sha256": sha256(audio[0])}
    result["ok"] = not result["issues"]
    return result


def run_with_retry(operation, attempts: int = MAX_RETRIES, base_delay: float = 1.0):
    attempts = max(1, min(attempts, MAX_RETRIES))
    last = None
    for number in range(1, attempts + 1):
        try:
            return operation(number)
        except Exception as exc:  # caller receives the final cause
            last = exc
            if number == attempts:
                raise
            time.sleep(base_delay * (2 ** (number - 1)))
    raise last  # pragma: no cover


def _tts_imports():
    sys.path.insert(0, "/data/.openclaw/tools/two-voice-tts")
    import edge_tts, imageio_ffmpeg
    return edge_tts, imageio_ffmpeg


async def render_episode(episode: str, retries: int = MAX_RETRIES, force: bool = False) -> Path:
    """Render script turns with resumable parts and an atomic final MP3."""
    gate = preflight(episode, require_audio=False, enforce_review=True)
    if not gate["ok"]:
        raise ValueError("preflight failed: " + "; ".join(gate["issues"]))
    script = ROOT / "episodes" / episode / "script.md"
    output_dir = script.parent
    output = next((p for p in output_dir.glob("*.mp3") if p.name != "output.mp3"), output_dir / f"episode-{episode}.mp3")
    parts = output_dir / "parts-robust"
    parts.mkdir(exist_ok=True)
    turns = parse_turns(script)
    plan = hashlib.sha256(script.read_bytes()).hexdigest()
    plan_file = parts / "render-plan.json"
    old_plan = json.loads(plan_file.read_text()) if plan_file.exists() else {}
    if old_plan.get("script_sha256") != plan:
        force = True
        for old in parts.glob("*.mp3"):
            old.unlink()
    edge_tts, imageio_ffmpeg = _tts_imports()
    voices = {"host": "en-US-AvaMultilingualNeural", "rowan": "en-GB-SoniaNeural", "guest": "en-GB-RyanNeural"}
    rates = {"host": "-3%", "rowan": "-5%", "guest": "-5%"}
    with PipelineLock(timeout=0):
        ledger = load_ledger()
        record = ledger.setdefault("episodes", {}).setdefault(episode, {"status": "planned", "transitions": []})
        if record.get("status") in {"planned", "review_pending"}:
            if record.get("status") == "planned":
                transition(ledger, episode, "review_pending", "awaiting three-reviewer gate")
                save_ledger(ledger)
            transition(ledger, episode, "reviewed", "three-reviewer gate passed")
        transition(ledger, episode, "rendering", "render started")
        record["attempts"] = record.get("attempts", 0) + 1
        save_ledger(ledger)
        files = []
        try:
            for index, (role, text) in enumerate(turns):
                part = parts / f"{index:04d}-{role}.mp3"
                if not force and part.exists() and part.stat().st_size > 1000:
                    files.append(part)
                    continue
                temporary = part.with_suffix(part.suffix + f".tmp.{os.getpid()}")
                async def synth(_: int):
                    await edge_tts.Communicate(text, voices[role], rate=rates[role]).save(str(temporary))
                    if not temporary.exists() or temporary.stat().st_size <= 1000:
                        raise IOError(f"empty TTS output for turn {index}")
                await _async_retry(synth, retries)
                os.replace(temporary, part)
                files.append(part)
            concat = parts / "concat.txt"
            atomic_write(concat, "".join(f"file '{p.resolve().as_posix()}'\n" for p in files))
            temporary_output = output.with_suffix(output.suffix + f".tmp.{os.getpid()}")
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c:a", "libmp3lame", "-b:a", "128k", str(temporary_output)], check=True, capture_output=True)
            if not temporary_output.exists() or temporary_output.stat().st_size <= 1000:
                raise IOError("ffmpeg produced an empty output")
            os.replace(temporary_output, output)
            atomic_json(plan_file, {"schema_version": 1, "script_sha256": plan, "turns": len(turns), "parts": [p.name for p in files], "completed_at": utc_now()})
            transition(ledger, episode, "rendered", "atomic render complete")
            record["artifacts"] = {"audio": str(output.relative_to(ROOT)), "audio_sha256": sha256(output), "turns": len(turns)}
            save_ledger(ledger)
            return output
        except Exception as exc:
            if 'temporary_output' in locals():
                with contextlib.suppress(FileNotFoundError):
                    temporary_output.unlink()
            record.setdefault("errors", []).append({"at": utc_now(), "error": repr(exc)})
            transition(ledger, episode, "failed", "render failed")
            save_ledger(ledger)
            raise


async def _async_retry(operation, attempts: int):
    attempts = max(1, min(attempts, MAX_RETRIES))
    for n in range(1, attempts + 1):
        try:
            return await operation(n)
        except Exception:
            if n == attempts:
                raise
            await asyncio.sleep(2 ** (n - 1))


def verify_feed(feed: Path | str, remote: str | None = None, timeout: float = 15.0) -> dict[str, Any]:
    """Verify local RSS/files and optionally the deployed feed over HTTP."""
    feed_path = Path(feed) if not str(feed).startswith(("http://", "https://")) else None
    result: dict[str, Any] = {"ok": False, "feed": str(feed), "checks": [], "issues": [], "warnings": []}
    try:
        xml = feed_path.read_bytes() if feed_path else urllib.request.urlopen(str(feed), timeout=timeout).read()
        root = ET.fromstring(xml)
        if remote and feed_path:
            remote_feed = remote.rstrip("/") + "/feed.xml"
            try:
                with urllib.request.urlopen(remote_feed, timeout=timeout) as response:
                    remote_root = ET.fromstring(response.read())
                    if response.status != 200 or not remote_root.findall(".//item"):
                        raise IOError(f"HTTP {response.status} or no RSS items")
                result["checks"].append({"name": "remote_feed", "url": remote_feed, "http": 200})
            except Exception as exc:
                result["issues"].append(f"remote feed check failed for {remote_feed}: {exc}")
        items = root.findall(".//item")
        guids = [item.findtext("guid", "") for item in items]
        if len(guids) != len(set(guids)):
            result["issues"].append("duplicate RSS GUID")
        result["checks"].append({"name": "feed_parse", "ok": True, "items": len(items)})
        for item in items:
            legacy_item = item.findtext("{http://www.itunes.com/dtds/podcast-1.0.dtd}episode") == "1"
            enclosure = item.find("enclosure")
            if enclosure is None or not enclosure.get("url"):
                result["issues"].append("RSS item missing enclosure")
                continue
            url, length = enclosure.get("url"), int(enclosure.get("length", "-1"))
            if feed_path:
                local = feed_path.parent / Path(urllib.parse.urlparse(url).path).name
                if not local.exists():
                    result["issues"].append(f"missing local enclosure {local.name}")
                elif length != local.stat().st_size:
                    result["issues"].append(f"enclosure length mismatch for {local.name}")
            if remote:
                remote_url = remote.rstrip("/") + "/" + Path(urllib.parse.urlparse(url).path).name
                req = urllib.request.Request(remote_url, headers={"Range": "bytes=0-1023"})
                try:
                    with urllib.request.urlopen(req, timeout=timeout) as response:
                        status = response.status
                        body = response.read(1024)
                    if status not in (200, 206) or not body:
                        result["issues"].append(f"remote audio check failed for {remote_url}: HTTP {status}")
                    else:
                        content_range = response.headers.get("Content-Range", "")
                        match = re.search(r"/([0-9]+)$", content_range)
                        if match and int(match.group(1)) != length:
                            result["issues"].append(f"remote audio length mismatch for {remote_url}")
                        result["checks"].append({"name": "remote_audio", "url": remote_url, "http": status})
                except Exception as exc:
                    result["issues"].append(f"remote audio check failed for {remote_url}: {exc}")
            notes_link = item.find("content:encoded", {"content": "http://purl.org/rss/1.0/modules/content/"})
            if notes_link is None:
                # ElementTree's expanded name is easier to handle portably.
                notes_link = next((x for x in item if x.tag.endswith("encoded")), None)
            if notes_link is not None:
                hrefs = re.findall(r'href=["\']([^"\']+notes\.md)["\']', notes_link.text or "")
                if feed_path:
                    for href in hrefs:
                        local_notes = feed_path.parent / Path(urllib.parse.urlparse(href).path).name
                        if not local_notes.exists():
                            target = result["warnings"] if legacy_item else result["issues"]
                            target.append(f"missing local notes file {local_notes.name}")
                if remote:
                    for href in hrefs:
                        notes_url = remote.rstrip("/") + "/" + Path(href).name
                        try:
                            with urllib.request.urlopen(notes_url, timeout=timeout) as response:
                                if response.status != 200:
                                    raise IOError(f"HTTP {response.status}")
                            result["checks"].append({"name": "remote_notes", "url": notes_url, "http": 200})
                        except Exception as exc:
                            target = result["warnings"] if legacy_item else result["issues"]
                            target.append(f"remote notes check failed for {notes_url}: {exc}")
    except Exception as exc:
        result["issues"].append(f"feed parse/check failed: {exc}")
    result["ok"] = not result["issues"]
    return result


def publish_local(episodes: list[str] | None = None, remote: str | None = None) -> dict[str, Any]:
    """Build the checked-in local feed and verify it; never performs a git push.

    Already-published legacy episodes are treated as imported history. Any
    episode still in a production state must pass the review gate and audio
    preflight before it can enter the local feed.
    """
    try:
        from .publish_feed import main as build_feed
    except ImportError:
        from publish_feed import main as build_feed
    ledger = load_ledger()
    selected = episodes or sorted(load_manifest().get("episodes", {}))
    checks = []
    for number in selected:
        record = ledger.get("episodes", {}).get(number, {})
        if record.get("status") != "published":
            check = preflight(number, require_audio=True, enforce_review=True)
            checks.append(check)
            if not check["ok"]:
                raise ValueError(f"publish preflight failed for {number}: {'; '.join(check['issues'])}")
    with PipelineLock(timeout=0):
        build_feed()
        result = verify_feed(ROOT / "feed-site" / "feed.xml", remote)
        if not result["ok"]:
            raise ValueError("local publication verification failed: " + "; ".join(result["issues"]))
        for number in selected:
            record = ledger.setdefault("episodes", {}).setdefault(number, {"status": "planned", "transitions": []})
            if record.get("status") == "rendered":
                transition(ledger, number, "verified", "local feed checks passed")
            if record.get("status") == "verified":
                transition(ledger, number, "published", "local feed built and verified; remote push remains manual")
        save_ledger(ledger)
    return {"ok": True, "episodes": selected, "preflight": checks, "verification": result, "external_push": "not performed"}


def status() -> dict[str, Any]:
    ledger = load_ledger()
    report = {"generated_at": utc_now(), "ledger_updated_at": ledger.get("updated_at"), "episodes": {}, "healthy": True}
    for number, rec in sorted(ledger.get("episodes", {}).items()):
        # Legacy published episodes predate checked-in scripts/review panels;
        # retain their audit issues without treating them as an active failure.
        pre = preflight(number, require_audio=False, enforce_review=False)
        is_legacy = rec.get("status") == "published"
        entry = {"state": rec.get("status"), "attempts": rec.get("attempts", 0), "errors": rec.get("errors", [])[-3:], "preflight_ok": True if is_legacy else pre["ok"], "issues": [] if is_legacy else pre["issues"]}
        if is_legacy and pre["issues"]:
            entry["legacy_audit_issues"] = pre["issues"]
        report["episodes"][number] = entry
        if rec.get("status") in {"failed", "blocked", "rendering"} or (not is_legacy and not pre["ok"]):
            report["healthy"] = False
    report["lock"] = dict(lock_status(), path=str(LOCK_PATH))
    if report["lock"]["active"]:
        report["healthy"] = False
    return report


def watchdog(max_render_minutes: int = 120) -> dict[str, Any]:
    report = status()
    stale = []
    ledger_time = datetime.fromisoformat(report["ledger_updated_at"].replace("Z", "+00:00")) if report.get("ledger_updated_at") else datetime.now(timezone.utc)
    age_minutes = (datetime.now(timezone.utc) - ledger_time).total_seconds() / 60
    for number, rec in report["episodes"].items():
        if rec["state"] == "rendering" and age_minutes > max_render_minutes:
            stale.append(f"episode {number} rendering for {age_minutes:.1f} minutes")
    report["stale"] = stale
    report["healthy"] = report["healthy"] and not stale
    return report


def print_result(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("inventory"); p.add_argument("--episode")
    p = sub.add_parser("reconcile"); p.add_argument("--episode"); p.add_argument("--write", action="store_true")
    p = sub.add_parser("preflight"); p.add_argument("episode"); p.add_argument("--audio", action="store_true"); p.add_argument("--no-review", action="store_true")
    p = sub.add_parser("review"); p.add_argument("episode"); p.add_argument("--panel", type=Path)
    p = sub.add_parser("render"); p.add_argument("episode"); p.add_argument("--force", action="store_true"); p.add_argument("--retries", type=int, default=MAX_RETRIES)
    p = sub.add_parser("verify"); p.add_argument("feed", nargs="?", default=str(ROOT / "feed-site" / "feed.xml")); p.add_argument("--remote")
    p = sub.add_parser("publish"); p.add_argument("--episode", action="append", dest="episodes"); p.add_argument("--remote", help="optional deployed site base URL to verify; no upload is performed")
    sub.add_parser("status")
    p = sub.add_parser("watchdog"); p.add_argument("--max-render-minutes", type=int, default=120)
    p = sub.add_parser("unlock"); p.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = None
        if args.command == "inventory":
            with PipelineLock(timeout=0):
                result = inventory(args.episode)
        elif args.command == "reconcile":
            if args.write:
                with PipelineLock(timeout=0):
                    result = reconcile(args.episode, True)
            else:
                result = reconcile(args.episode, False)
        elif args.command == "preflight": result = preflight(args.episode, args.audio, not args.no_review)
        elif args.command == "review":
            with PipelineLock(timeout=0):
                result = record_review(args.episode, args.panel)
        elif args.command == "render": result = {"ok": True, "output": str(asyncio.run(render_episode(args.episode, args.retries, args.force)))}
        elif args.command == "verify": result = verify_feed(args.feed, args.remote)
        elif args.command == "publish": result = publish_local(args.episodes, args.remote)
        elif args.command == "status": result = status()
        elif args.command == "watchdog": result = watchdog(args.max_render_minutes)
        elif args.command == "unlock": unlock(args.force); result = {"unlocked": True}
        print_result(result)
        if args.command in {"reconcile", "preflight", "review", "verify", "publish", "status", "watchdog"}:
            return 0 if result.get("ok", result.get("healthy", True)) else 1
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
